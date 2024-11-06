from openai import OpenAI
import os
import json

with open("OAI_CONFIG_LIST", "r") as file:
    json_str = file.read()
config_list = json.loads(json_str)


client = OpenAI(api_key=config_list[0]['api_key'],base_url=config_list[0]['base_url'])

msg = """
hello
"""

MODEL = "gpt-4o"
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": msg},

    ],
    temperature=0.2,
)

print(response.choices[0].message)
# response.model_dump_json() 返回的是一个 JSON 字符串，
# print(json.dumps(json.loads(response.model_dump_json()), indent=4))
