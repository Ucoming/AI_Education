import numpy as np
from openai import OpenAI
import pymysql
import pandas as pd

from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

client = OpenAI(api_key=os.getenv("api_key"))


# 获取与用户问题最相似的问题
def get_similar_questions(user_question, top_n=5):
    # 连接到数据库
    connection = pymysql.connect(
        host='127.0.0.1',
        user=os.getenv("name"),
        password=os.getenv("password"),
        database='education_test1',
        charset='utf8mb4'
    )

    try:  
        # 从数据库中获取问题列
        query = "SELECT question FROM t1"
        df = pd.read_sql(query, connection)

        # 计算每个问题与用户问题的相似度
        similarity_scores = []
        for question in df['question']:
            similarity = calculate_similarity(user_question, question)
            similarity_scores.append((question, similarity))

        # 按相似度排序并获取前 top_n 个问题
        similar_questions = sorted(similarity_scores, key=lambda x: x[1], reverse=True)[:top_n]

        return similar_questions

    finally:
        # 关闭数据库连接
        connection.close()


# 生成文本嵌入
def get_text_embedding(text):
    text = text.replace("\n", " ")
    embedding = client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
    return np.array(embedding)


# 计算两个文本的相似度
def calculate_similarity(text1, text2):
    embedding1 = get_text_embedding(text1)
    embedding2 = get_text_embedding(text2)

    # 计算余弦相似度
    cosine_similarity = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    return cosine_similarity


if __name__ == "__main__":
    # 示例调用
    user_question = "摄影技术对艺术有何影响？"
    similar_questions = get_similar_questions(user_question)
    print("最相似的问题：")
    for question, similarity in similar_questions:
        print(f"问题: {question}，相似度: {similarity}")
