import json
import random
import re
import time
import uuid

from core import Chat, Database, Person
from prompts import BACKGROUND, EPITAPH, EVAL, EVENTS, RULES, SUM


class Moderator:
    #初始化
    def __init__(self, expiration=1800, debug=False) -> None:
        #存储和管理玩家的状态信息，如背景、属性core/Database.py
        self.redis = Database(time_out=expiration, debug=debug)
        #生成游戏的文本对话
        self.chat = Chat(max_tokens=4000, debug=debug)
        #玩家数据在数据库中的过期时间
        self.expiration = expiration
        self.option_indicator = r'\n\d+\. '
        #随机生成了一个人物
        self.person = Person()

    #初始化玩家并将玩家信息存储在数据库中
    def init_player(self, session_id):
        person = Person()
        print(person)
        data_dict = {'time': time.perf_counter(), 'person': str(person)}
        self.redis.update(session_id, data_dict)
        return json.loads(str(person))

    #生成背景方法
    async def generate_background(self, session_id):
        data_dict = self.redis.fetch(session_id)
        #chat_list是和chatCPT对话的内容 规则+背景+玩家信息
        # print(data_dict['person'])
        chat_list = [RULES, BACKGROUND, ('user', str(data_dict['person']))]
        chat_stream = self.chat(chat_list)
        context = ''
        async for text in chat_stream:
            context += text
            yield text
        data_dict['background'] = context

        # summarize background
        chat_list = [('user', SUM[1].format(context))]
        chat_stream = self.chat(chat_list)
        sum_context = ''
        async for text in chat_stream:
            sum_context += text
        data_dict['background_sum'] = sum_context

        self.redis.update(session_id, data_dict)

    #生成事件方法
    async def generate_events(self, session_id):
        data_dict = self.redis.fetch(session_id)
        #根据年龄生成事件类型
        event_type = self.person.get_event_by_age(data_dict['person']['年龄'])
        chat_list = [
            RULES, EVENTS, ('user', data_dict['background']),
            ('user', str(data_dict['person'])), ('user', event_type)
        ]
        chat_stream = self.chat(chat_list)
        context = ''
        async for text in chat_stream:
            context += text
            yield text
        #分割事件和选项
        event, option = self.parse_events(context)
        event_data = {'event': event, 'option': option}
        if 'events' in data_dict:
            data_dict['events'].append(event_data)
        else:
            data_dict['events'] = [event_data]
        self.redis.update(session_id, data_dict)

    #评估玩家选择方法：根据玩家选择评估游戏时间结果并更新玩家状态信息
    async def evaluate_selection(self, session_id, selection: int):
        data_dict = self.redis.fetch(session_id)
        assert selection > 0 and selection <= 5
        # format input
        #格式化输入，将选择和相关信息添加到对话列表中
        selection = f'### 你的选择:\n**{selection}**'
        #最近发生的一次事件中用户的选项
        options = data_dict['events'][-1]['option']
        options = f'### 选项:\n{options}'
        person = str(data_dict['person'])
        person = f'### 你的基础信息：\n{person}'

        #获取用户选择后产生的结果
        chat_list = [
            RULES, EVAL, ('user', data_dict['events'][-1]['event']),
            ('user', person), ('user', options), ('user', selection)
        ]
        chat_stream = self.chat(chat_list)
        context = ''
        async for text in chat_stream:
            context += text
            yield text
        data_dict['events'][-1]['result'] = context

        #汇总事件信息
        # summarize events
        sum_content = '\n'.join(
            [data_dict['events'][-1]['event'], options, selection, context])
        chat_list = [('user', SUM[1].format(sum_content))]
        chat_stream = self.chat(chat_list)
        sum_context = ''
        async for text in chat_stream:
            sum_context += text
        data_dict['events'][-1]['sum'] = sum_context

        #玩家每做出一次选择，年龄会增加
        # update age
        added_age = random.randint(5, 10)
        data_dict['person']['年龄'] += added_age
        # update attribute
        self.parse_eval(session_id, data_dict, context)

    #生成墓志铭方法
    async def generate_epitaph(self, session_id):
        data_dict = self.redis.fetch(session_id)
        pre_prompt = '### 玩家事件(如果没有内容则表示当前还没有历史事件)\n***\n'
        if 'events' in data_dict:
            history = []
            for event in data_dict['events']:
                if 'sum' in event:
                    history.append(event['sum'])
                else:
                    continue
            history = '\n- '.join(history)
            history = pre_prompt + history + '\n```'
        else:
            history = pre_prompt + '\n```'
        person = '### 玩家属性 \n' + str(data_dict['person'])
        background = '### 玩家背景 \n' + data_dict['background_sum']
        whole_life = '\n'.join([person, background, history])
        chat_list = [EPITAPH, ('user', whole_life)]
        chat_stream = self.chat(chat_list)
        context = ''
        async for text in chat_stream:
            context += text
            yield text

    #解析事件文本方法
    def parse_events(self, event: str):
        start = re.search(self.option_indicator, event).start() + 1
        event, options = event[:start], event[start:]
        #返回事件描述和选项
        return event, options

    #解析评估结果方法
    def parse_eval(self, session_id, data_dict: dict, results: str):
        begin_id = results.find('属性')
        results = results[begin_id:].replace("'", '')
        pattern = r'\s*(\w+):\s*(\d+)'
        matches = re.findall(pattern, results)
        if not matches:
            raise ValueError(f'mis pattern in: {results}')

        result_dict = {}
        for attribute, value in matches:
            value = int(value)
            value = 10 if value >= 10 else value
            value = 0 if value <= 0 else value
            result_dict[attribute] = value
        data_dict['person']['属性'] = result_dict
        # update person attribute
        self.redis.update(session_id, data_dict)

    #判断玩家是否存活的方法
    def is_alive(self, session_id) -> bool:
        data_dict = self.redis.fetch(session_id)
        person = data_dict['person']
        if person['年龄'] >= 90:
            return False
        if person['属性']['健康'] <= 0:
            return False
        if person['属性']['幸福度'] <= 0:
            return False
        return True

    #获取解析的事件和选项
    def get_parsed_event(self, session_id):
        data_dict = self.redis.fetch(session_id)
        print(data_dict)
        event = data_dict['events'][-1]['event']
        option = data_dict['events'][-1]['option']
        return event, option
    
    #获取玩家信息
    def get_person_info(self, session_id):
        data_dict = self.redis.fetch(session_id)
        return data_dict['person']
    
    def get_custom_info(self,session_id,message):
        data_dict = self.redis.fetch(session_id)
        data_dict['message'] = message
        print("-----comein success-----")
        print(data_dict['message'])
        return data_dict['message']


if __name__ == '__main__':
    import asyncio

    async def iterate_stream(stream):
        async for _ in stream:
            continue

    moderator = Moderator(debug=True)

    session_id = str(uuid.uuid4())
    session_id = '5b845b00-a839-48f5-8e03-0f38e8cb16f'
    print(session_id)

    moderator.init_player(session_id)
    asyncio.run(iterate_stream(moderator.generate_background(session_id)))

    while True:
        if not moderator.is_alive(session_id):
            break
        asyncio.run(iterate_stream(moderator.generate_events(session_id)))
        #获取玩家的选择
        selection = input()
        asyncio.run(
            iterate_stream(
                moderator.evaluate_selection(session_id, int(selection))))
    asyncio.run(iterate_stream(moderator.generate_epitaph(session_id)))
