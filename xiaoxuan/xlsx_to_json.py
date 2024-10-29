## 读取xlsx文件，将数据转化为json格式
import pandas as pd
import json


def xlsx_to_json(file_path, sheet_name, output_file):
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    data = df.to_dict(orient='records')
    with open(output_file, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data from sheet '{sheet_name}' has been converted to JSON and saved to '{output_file}'.")


if __name__ == "__main__":
    xlsx_file = r"D:\Scientific_Research\Education_Agent_Design\Education_part1\answer.xlsx"
    sheet_name = "Sheet1"
    output_json = "example.json"
    xlsx_to_json(xlsx_file, sheet_name, output_json)