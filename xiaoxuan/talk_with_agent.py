# --*-- coding: utf-8 --*--
import json

from dotenv import load_dotenv
import os
import openai
from extract_pdf import extract_text_from_pdf

load_dotenv()

api_key = os.getenv("API_KEY")
client = openai.OpenAI(api_key=api_key)

os.environ["http_proxy"] = os.getenv("http_proxy")
os.environ["https_proxy"] = os.getenv("https_proxy")


def chat_with_gpt(messages, model="gpt-4o"):
    response = client.chat.completions.create(model=model, messages=messages)
    return response.choices[0].message.content


## 从llm的回答中提取出json
def extract_json_from_llm_response(response):
    start_index = response.find("```json") + len("```json")
    end_index = response.find("```", start_index)
    json_str = response[start_index:end_index]
    return json.loads(json_str)


if __name__ == "__main__":
    # 读取pdf中的内容
    text = extract_text_from_pdf(r"D:\Scientific_Research\Education_Agent_Design\课程大纲&教案&逐字稿&习题.pdf")

    # 读取txt文件
    with open("prompt.txt", "r", encoding="utf-8") as f:
        prompt = f.read()

    prompt = prompt + text
    messages = [
        {"role": "system", "content": "You are an excellent teacher."},
        {"role": "user", "content": prompt},
    ]

    ## 保存到json文件中
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(extract_json_from_llm_response(chat_with_gpt(messages)), f, ensure_ascii=False)

    print("Done!")
