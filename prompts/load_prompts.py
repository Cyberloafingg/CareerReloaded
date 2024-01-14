# init overall rules
with open('./prompts/rules.txt', encoding='utf-8') as fp:
    rules_prompt = fp.readlines()
rules_prompt = ''.join(rules_prompt)
# print(rules_prompt)
RULES = ('system', rules_prompt)

# init background story
with open('./prompts/background.txt', encoding='utf-8') as fp:
    background_prompt = fp.readlines()
background_prompt = ''.join(background_prompt)
BACKGROUND = ('system', background_prompt)

# init events
with open('./prompts/events.txt', encoding='utf-8') as fp:
    events_prompt = fp.readlines()
events_prompt = ''.join(events_prompt)
EVENTS = ('system', events_prompt)

# init evaluation
with open('./prompts/evaluation.txt', encoding='utf-8') as fp:
    eval_prompt = fp.readlines()
eval_prompt = ''.join(eval_prompt)
EVAL = ('system', eval_prompt)

# init summarization
with open('./prompts/summarization.txt', encoding='utf-8') as fp:
    sum_prompt = fp.readlines()
sum_prompt = ''.join(sum_prompt)
SUM = ('system', sum_prompt)

# init epitaph
with open('./prompts/epitaph.txt', encoding='utf-8') as fp:
    epitaph_prompt = fp.readlines()
epitaph_prompt = ''.join(epitaph_prompt)
EPITAPH = ('system', epitaph_prompt)
