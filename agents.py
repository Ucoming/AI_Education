from typing import List, Dict
import autogen
from openai import OpenAI

class EducationAgents:
    def __init__(self, config_list):
        self.config_list = config_list
        
        # 初始化所有agents ,guider使用OpenAI接口    
        self.welcome = """你是一个AI教育引导者。你的职责是：
            1. 提供友好的欢迎语
            2. 总结本次要学习的内容主题，为本次学习提供一个清晰的介绍和引导
            3. 从数据库中选择3-5个适合初学者的问题推荐
            4. 创建能激发用户思考的引导性问题
            """

        self.reviewer_guider = """你是一个教育引导者和知识总结者。你的职责是：
            1. 总结用户已经学习过的知识点，帮助用户回顾和巩固
            2. 分析已学知识点之间的关联性和层次关系
            3. 基于已学内容，推荐接下来适合学习的知识点
            4. 设计引导性问题，帮助用户:
                - 加深对已学内容的理解
                - 建立知识点之间的联系
                - 思考知识点的实际应用
            5. 根据用户的学习进度和表现，调整推荐的学习路径
            6. 提供积极的反馈和鼓励，保持用户的学习动力
            """

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
            "welcome": self.welcome,
            "guider": self.reviewer_guider,
            "teacher": self.teacher,
            "evaluator": self.evaluator,
            "user_proxy": self.user_proxy
        }
    def openai_completion(self, message: str, system_message: str = "You are a helpful assistant.") -> str:
        """使用OpenAI API生成回复
        Args:
            message: 用户输入的消息
            system_message: 系统提示信息,默认为通用助手 
        Returns:
            str: OpenAI生成的回复文本
        """

        
        client = OpenAI(
            api_key=self.config_list[0]['api_key'],
            base_url=self.config_list[0]['base_url']
        )
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": message
                }
            ]
        )
        
        return response.choices[0].message.content
     