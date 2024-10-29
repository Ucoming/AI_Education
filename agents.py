from typing import List, Dict
import autogen

class EducationAgents:
    def __init__(self, config_list):
        self.config_list = config_list
        
        # 初始化所有agents
        self.guider = autogen.AssistantAgent(
            name="Guider",
            system_message="""你是一个教育引导者。你的职责是：
            1. 提供友好的欢迎语
            2. 从数据库中选择3-5个适合初学者的问题推荐
            3. 创建能激发用户思考的引导性问题
            4. 追踪用户的学习进度""",
            llm_config={"config_list": config_list}
        )

        self.teacher = autogen.AssistantAgent(
            name="Teacher",
            system_message="""你是一个专业的教师。你的职责是：
            1. 根据用户提问提供详细的解答
            2. 通过对话方式确保用户理解内容
            3. 当用户表示理解时，将信息传递给评估者
            4. 采用循序渐进的教学方法""",
            llm_config={"config_list": config_list}
        )

        self.evaluator = autogen.AssistantAgent(
            name="Evaluator",
            system_message="""你是一个严格的评估者。你的职责是：
            1. 评估用户的学习进度
            2. 生成测评题目
            3. 评估用户的回答
            4. 提供具体的改进建议
            5. 决定是否将知识点标记为已学习""",
            llm_config={"config_list": config_list}
        )

        self.user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="ALWAYS",
            system_message="你是一个积极学习的学生，会提出问题并与教师互动。",
            code_execution_config=False
        )

    def get_agents(self) -> Dict:
        return {
            "guider": self.guider,
            "teacher": self.teacher,
            "evaluator": self.evaluator,
            "user_proxy": self.user_proxy
        } 