from typing import List, Dict
import autogen
from agents import EducationAgents


class MultiAgentEducationSystem:
    def __init__(self, config_list: List, qa_database: Dict):
        self.agents = EducationAgents(config_list)
        self.qa_database = qa_database
        self.qa_list_matched = set()  # 存储匹配到的问题ID
        
    def similarity_match(self, query: str, n: int = 3) -> List[Dict]:
        """根据用户问题匹配数据库中最相似的n个QA对, 及其id值"""
        # TODO: 实现相似度匹配算法
        pass
    def get_beginner_questions(self) -> List[Dict]:
        """获取所有入门级别的问题"""
        beginner_questions = []
        for qa in self.qa_database:
            if qa.get("学习进度") == "入门阶段":
                beginner_questions.append({
                    "question": qa["问题"],
                    "answer": qa["答案"]
                })
        return beginner_questions
    
    def generate_welcome_message(self) -> str:
        """生成开场白
        
        Args:
            agents: 包含所有agent的字典
            
        Returns:
            str: 生成的开场白文本
        """
        beginner_questions = self.get_beginner_questions()
        guider = self.agents.get_agents()["guider"]
        
        welcome_prompt = f"""
        请生成一段友好的开场白，包括:
        1. 欢迎语
        2. 从下面入门问题列表中总结并推荐3-5个适合初学者的问题
        3. 通过鼓励性的引导语，激发用户学习兴趣
        
        入门问题列表：
        {beginner_questions}
        """
        
        welcome_word = guider.generate_response(welcome_prompt)
        return welcome_word
    def get_recommended_questions(self, n: int = 3) -> List[Dict]:
        """从未学习的知识点中推荐n个问题
        
        Args:
            n: 推荐的问题数量，默认为3
            
        Returns:
            List[Dict]: 包含问题和答案的字典列表
        """
        # 获取所有未学习的问题
        unlearned_questions = []
        for qa_id, qa in self.qa_database.items():
            if qa.get("learned", "no") == "no":
                qa_copy = qa.copy()
                qa_copy["id"] = qa_id
                unlearned_questions.append(qa_copy)
                
        # 如果未学习的问题少于n个,返回所有未学习的问题
        if len(unlearned_questions) <= n:
            return unlearned_questions
            
        # 否则随机选择n个问题
        import random
        recommended = random.sample(unlearned_questions, n)
        
        return [{
            "id": qa["id"],
            "question": qa["问题"],
            "answer": qa["答案"]
        } for qa in recommended]
    def generate_guiding_questions(self, qa_ids: List[str]) -> str:
        """根据知识点生成引导性问题
        
        Args:
            qa_ids: 知识点ID列表
            
        Returns:
            str: 生成的引导性问题
        """
        qa_contents = []
        for qa_id in qa_ids:
            qa_content = self.qa_database[qa_id]
            qa_contents.append({
                "问题": qa_content["问题"],
                "答案": qa_content["答案"]
            })
            
        guider = self.agents.get_agents()["guider"]
        
        guiding_prompt = f"""
        基于以下知识点内容，生成3-4个引导性问题，帮助学生逐步理解这些相关概念：
        
        知识点列表：
        {qa_contents}
        
        生成的问题应该：
        1. 由浅入深，循序渐进
        2. 启发思考，而不是直接给出答案
        3. 联系实际应用场景
        4. 引导学生发现这些知识点之间的联系
        5. 综合运用多个知识点
        """
        
        guiding_questions = guider.generate_response(guiding_prompt)
        return guiding_questions

    def label_learned_point(self, qa_id: str):
        """标记某个知识点为已学习"""
        if qa_id in self.qa_database and self.qa_database[qa_id]["learned"] == "no":
            self.qa_database[qa_id]["learned"] = "yes"
            self.qa_list_matched.add(qa_id)
            print(f"知识点 {qa_id} 已标记为已学习")
            print(f"当前已学习知识点: {sorted(list(self.qa_list_matched))}")



    def calc_progress_bar(self) -> float:
        """计算学习进度"""
        learned_count = len(self.qa_list_matched)
        total_count = len(self.qa_database)
        return (learned_count / total_count) * 100

    def start_learning_session(self):
        """开始学习会话"""
        agents = self.agents.get_agents()
        welcome_message = self.generate_welcome_message()
        print(welcome_message)
        
        
        i = 0
        while True:
            # 检查是否所有知识点都已学习
            if len(self.qa_list_matched) == len(self.qa_database):
                print("恭喜！你已完成所有学习内容！")
                break
            if i == 0:
                user_input = input("选择一个你想要学习的问题，或者输入一个你想要学习的问题：")
            else:
                recommended_questions = self.get_recommended_questions(5)
                guide_message = self.generate_guiding_questions(recommended_questions)
                print(guide_message)
                
                user_input = input("请输入你想要学习的问题：")
            QA_list_matched = self.similarity_match(user_input,5)
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

            # 启动对话
            
            agents["user_proxy"].initiate_chat(
                manager,
                message=user_input
            )
            
            # 标记QA_list_matched中的知识点为已学习
            for qa_id in QA_list_matched:
                self.label_learned_point(qa_id)

            # 更新进度
            progress = self.calc_progress_bar()
            print(f"当前学习进度: {progress:.2f}%") 
            i += 1