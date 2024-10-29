import autogen

# OpenAI API配置
config_list = autogen.config_list_from_json(env_or_file="OAI_CONFIG_LIST")


# 示例QA数据库, 实际使用时从数据库中读取
qa_database = {
    "q1": {
        "question": "什么是数据库索引？",
        "answer": "数据库索引是一种数据结构，用于加快数据库查询速度...",
        "learned": "no"
    },
    "q2": {
        "question": "什么是事务的ACID特性？",
        "answer": "ACID是数据库事务的四个基本特性：原子性、一致性、隔离性和持久性...",
        "learned": "no"
    }
    # ... 更多QA对
}

def main():
    from multi_agent_edu_system import MultiAgentEducationSystem
    
    # 创建教育系统实例
    edu_system = MultiAgentEducationSystem(config_list, qa_database)
    
    # 开始学习会话
    edu_system.start_learning_session()

if __name__ == "__main__":
    main()
