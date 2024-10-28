import pandas as pd
import json


def json_to_excel(json_file_path, excel_file_path):
    """
    将 JSON 文件转换为 Excel 文件（.xlsx 格式）。

    参数:
    - json_file_path: JSON 文件路径
    - excel_file_path: 输出的 Excel 文件路径
    """
    # 读取 JSON 文件
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # 将 JSON 数据转换为 DataFrame
    df = pd.DataFrame(data)

    # 将 DataFrame 写入 Excel 文件
    df.to_excel(excel_file_path, index=False)

    print(f"数据已成功保存到 {excel_file_path}")


if __name__ == "__main__":
    # 示例调用
    json_to_excel('output.json', 'output.xlsx')
