import autogen
import json
import pandas as pd

# OpenAI API配置
config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")

# 示例QA数据库, 实际使用时从数据库中读取，目前暂时导入本地json文件····················

# 从xiaoxuan/output.json读取QA数据
with open('xiaoxuan/output.json', 'r', encoding='utf-8') as f:
    qa_database = json.load(f)

# Convert JSON to DataFrame
df = pd.DataFrame(qa_database)

# Add learner_tag column with default value 0
df['learner_tag'] = 0
# Add id column with sequential numbers starting from 1
df['id'] = range(1, len(df) + 1)

# 以上内容未来将替换为从数据库中读取····························

qa_database = df

def main():
    from multi_agent_edu_system import MultiAgentEducationSystem
    
    # 创建教育系统实例
    edu_system = MultiAgentEducationSystem(config_list, qa_database)
    
    # 开始学习会话
    edu_system.start_learning_session()

if __name__ == "__main__":
    main()
