import pymysql
import json
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()


def insert_data_to_mysql(host, port, database, table_name, json_file_path, course_name):
    """
    插入JSON数据到MySQL表中，并为每条记录设置固定的course_name。

    参数:
    - host: 数据库主机地址
    - port: 数据库端口
    - database: 数据库名称
    - table_name: 目标表名称
    - json_file_path: JSON文件路径
    - course_name: 课程名称
    """
    # 获取数据库用户名和密码
    username = os.getenv("name")
    password = os.getenv("password")

    # 连接数据库
    connection = pymysql.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database=database,
        charset='utf8mb4'
    )

    try:
        # 打开JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # 插入数据
        with connection.cursor() as cursor:
            for item in data:
                sql = f"""
                INSERT INTO {table_name} (course_name, question, content_correlation, question_depth, learning_process, answer)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    course_name,
                    item["问题"],
                    item["内容相关性"],
                    item["问题深度"],
                    item["学习进度"],
                    item["答案"]
                ))

        # 提交更改
        connection.commit()

    finally:
        # 关闭数据库连接
        connection.close()

    print("数据插入完成！")


if __name__ == "__main__":
    # 示例调用
    insert_data_to_mysql(
        host='127.0.0.1',
        port=3306,
        database='education_test1',
        table_name='t1',
        json_file_path='output.json',
        course_name='摄影艺术'
    )