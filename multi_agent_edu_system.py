from typing import List, Dict
import autogen
from agents import EducationAgents
import pandas as pd
from openai import OpenAI


class MultiAgentEducationSystem:
    def __init__(self, config_list: List, qa_database: pd.DataFrame):
        self.agents = EducationAgents(config_list)
        self.config_list = config_list
        self.qa_database = qa_database
        
    def similarity_match(self, query: str, n: int = 3) -> List[Dict]:
        """根据用户问题匹配数据库中最相似的n个QA对, 及其id值
        
        Args:
            query: 用户输入的问题
            n: 返回的最相似问题数量
            
        Returns:
            List[Dict]: 包含id、问题、答案和相似度的字典列表
        """
        client = OpenAI(
            api_key=self.config_list[0]['api_key'],
            base_url=self.config_list[0]['base_url']
        )
        
        # 获取查询问题的embedding
        query_embedding = client.embeddings.create(
            input=[query], 
            model="text-embedding-3-small"
        ).data[0].embedding
        
        # 计算所有问题的embedding并计算相似度
        similarities = []
        for _, row in self.qa_database.iterrows():
            question_embedding = client.embeddings.create(
                input=[row['问题']], 
                model="text-embedding-3-small"
            ).data[0].embedding
            
            # 计算余弦相似度
            similarity = sum(a * b for a, b in zip(query_embedding, question_embedding)) / (
                (sum(a * a for a in query_embedding) * sum(b * b for b in question_embedding)) ** 0.5
            )
            
            similarities.append({
                'id': row['id'],
                'question': row['问题'],
                'answer': row['答案'],
                'similarity': similarity
            })
        
        # 按相似度排序并返回前n个结果
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:n]

    def get_beginner_questions(self) -> List[Dict]:
        """获取所有入门级别的问题"""
        beginner_questions = []
        # 使用DataFrame的查询方式
        beginner_df = self.qa_database[self.qa_database['学习进度'] == '入门阶段']
        for _, row in beginner_df.iterrows():
            beginner_questions.append({
                "question": row['问题'],
                "answer": row['答案']
            })
        return beginner_questions
    
    def generate_welcome_message(self) -> str:
        """生成开场白"""
        beginner_questions = self.get_beginner_questions()
        welcome_system = self.agents.get_agents()["welcome"]
        
        welcome_prompt = f"""
        请根据问题列表生成一段友好的开场白，包括:
        1. 欢迎语，这部分内容需要包含问候语，介绍自己的身份，并表达对用户学习的欢迎。比如："欢迎体验AI对话教育系统，我是你的AI教育引导者，你可以称呼我为小I。"
        2. 从下面入门问题列表中总结本次要学习的内容主题，并推荐3-5个适合初学者的问题
        3. 通过鼓励性的引导语，激发用户学习兴趣
        
        入门问题列表：
        {beginner_questions}
        """
        
        # 调用OpenAI API生成回复
        welcome_word = self.agents.openai_completion(welcome_prompt,system_message = welcome_system)
        
        return welcome_word

    def get_recommended_questions(self, n: int = 3) -> List[Dict]:
        """从未学习的知识点中推荐n个问题
        Args:
            n: 推荐的问题数量，默认为3
        Returns:
            List[Dict]: 包含问题和答案的字典列表
        """
        # 获取所有未学习的问题
        unlearned_df = self.qa_database[self.qa_database['learner_tag'] == 0]
        
        # 如果未学习的问题少于n个,返回所有未学习的问题
        if len(unlearned_df) <= n:
            result = []
            for _, row in unlearned_df.iterrows():

                result.append({
                    "id": row['id'],
                    "question": row['问题'],
                    "answer": row['答案']
                })
            return result
            
        # 否则随机选择n个问题
        sampled_df = unlearned_df.sample(n=n)
        
          
        return [{
            "id": row['id'],
            "question": row['问题'],
            "answer": row['答案']
        } for _, row in sampled_df.iterrows()]

    def generate_database_questions(self, qa: List[Dict]) -> str:
        """根据知识点生成引导性问题
        Args:
            qa: 知识点列表，每个知识点包含id、question和answer
        Returns:
            str: 生成的引导性问题
        """
        qa_contents = []
        for qa_item in qa:
            qa_contents.append({
                "问题": qa_item['question'],
                "答案": qa_item['answer']
            })
            
        reviewer_guider = self.agents.get_agents()["reviewer_guider"]
        
        guiding_prompt = f"""
        基于以下已学知识点，为用户进行总结，并结合未学知识点列表，为用户推荐接下来要学习的内容：
        已学知识点：
        {qa_contents}

        未学知识点列表：
        {qa_contents}
        
        生成的问题应该：
        1. 由浅入深，循序渐进
        2. 启发思考，而不是直接给出答案
        3. 联系实际应用场景
        4. 引导学生发现这些知识点之间的联系
        5. 综合运用多个知识点
        """
        
        guiding_questions = self.agents.openai_completion(guiding_prompt,system_message = reviewer_guider)
        return guiding_questions


    def calc_progress_bar(self) -> float:
        """计算学习进度"""
        # 统计learner_tag为1的记录数量
        learned_count = len(self.qa_database[self.qa_database['learner_tag'] == 1])
        total_count = len(self.qa_database)
        return (learned_count / total_count) * 100

    def start_learning_session(self):
        """开始学习会话"""
        agents = self.agents.get_agents()
        welcome_message = self.generate_welcome_message()

        i = 0
        while True:
            # 检查是否所有知识点都已学习
            if (self.qa_database['learner_tag'] == 1).all():
                print("恭喜！你已完成所有学习内容！")
                break

            if i == 0:
                user_input = input("选择一个你想要学习的问题，或者输入一个你想要学习的问题：")
            else:
                recommended_questions = self.get_recommended_questions(5) # 获取5个未学习的问题,用于生成引导性问题
                guide_message = self.generate_database_questions(recommended_questions)
                print(guide_message)
                
                user_input = input("请输入你想要学习的问题：")
            # 获取相似问题并标记为已学习
            QA_list_matched = self.similarity_match(user_input, 5)
            for qa_id in QA_list_matched:
                if qa_id in self.qa_database['id'].values:
                    self.qa_database.loc[self.qa_database['id'] == qa_id, 'learner_tag'] = 1
            # 创建群聊
            
            background_message = {
                "role": "system",
                "content": f"以下是需要教授的知识点列表：{QA_list_matched}"
            }

            groupchat = autogen.GroupChat(
                agents=[agents["teacher"], agents["evaluator"], agents["user_proxy"]],
                messages=[background_message],
                max_round=10
            )
            
            manager = autogen.GroupChatManager(groupchat=groupchat)

            # 启动对话并等待完成信号
            chat_result = agents["user_proxy"].initiate_chat(
                manager,
                message=user_input
            )
    
            # 更新进度
            progress = self.calc_progress_bar()
            print(f"当前学习进度: {progress:.2f}%") 
            i += 1