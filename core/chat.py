import asyncio
from typing import List

import semantic_kernel as sk
from semantic_kernel.connectors.ai import ChatRequestSettings
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion


class Chat:
    #链接到ChatGPT
    def __init__(self, max_tokens=2000, debug=False) -> None:
        self.debug = debug
        self.chat_request_settings = ChatRequestSettings(
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0.5,
            presence_penalty=0.5,
        )

        import os
        os.environ["http_proxy"] = "http://localhost:7890/"
        os.environ["https_proxy"] = "http://localhost:7890/"
        import openai
        openai.proxy = "http://127.0.0.1:7890/"
        api_key, org_id = sk.openai_settings_from_dot_env()
        self.oai_chat_service = OpenAIChatCompletion('gpt-3.5-turbo-16k',
                                                     api_key, org_id)

    def __call__(self, chat_list: List):
        return self.chat(chat_list)
    
    #向ChatGPT发送聊天列表，返回的text的ChatGPT回答的话
    async def chat(self, chat_list: List) -> None:
        #stream是OpenAI返回的话
        stream = self.oai_chat_service.complete_chat_stream_async(
            chat_list, self.chat_request_settings)

        idx = 0  # to skip the first word "assistant:"
        async for text in stream:
            if idx == 0:
                idx += 1
                continue
            if self.debug:
                print(text, end='')
                #将获取到的文本返回给调用方
            yield text
        if self.debug:
            print('')


if __name__ == '__main__':
    from core import Person
    from prompts import BACKGROUND, EVENTS, RULES
    person = Person()
    chat = Chat()
    chat_list = [RULES, BACKGROUND, ('user', str(person))]
    context = asyncio.run(chat.chat(chat_list))
    chat_list = [RULES, ('user', context), ('user', str(person)), EVENTS]
    context = asyncio.run(chat.chat(chat_list))
