from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import os
import pandas as pd
import re

os.environ["http_proxy"] = "http://127.0.0.1:33210"
os.environ["https_proxy"] = "http://127.0.0.1:33210"

class DocumentRAG:
    def __init__(self, openai_api_key):
        self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
        self.llm = ChatOpenAI(openai_api_key=openai_api_key)
        
    def load_pdf(self, pdf_path):
        # 加载PDF文件
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # 创建向量数据库
        self.vectorstore = FAISS.from_documents(splits, self.embeddings)
        
    def query(self, question: str) -> str:
        # 创建检索问答链
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )
        
        # 获取答案
        response = qa_chain.run(question)
        return response

    def generate_questions(self, num_main_questions: int = 5, num_sub_questions: int = 3, output_format: str = 'xlsx') -> None:
        """逐个生成主干问题和支线问题并保存到文件"""
        
        questions_data = []
        main_questions_set = set()  # 用于查重主干问题
        
        # 创建检索问答链
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever()
        )
        
        # 逐个生成主干问题
        for i in range(num_main_questions):
            main_prompt = f"""你是一个专业的教育专家。请基于文档内容生成一个重要的主干问题。
            这个问题应该能够考察读者对文档核心内容的理解。
            
            已有的主干问题：
            {[q['main_question'] for q in questions_data]}
            
            请生成一个不同于以上问题的新主干问题。直接输出问题，不需要任何前缀。"""
            
            while True:
                main_q = qa_chain.run(main_prompt).strip()
                # 去除可能的序号和多余标点
                main_q = re.sub(r'^[\d\.\s、]+', '', main_q)
                main_q = re.sub(r'[?？]+$', '？', main_q)
                
                if main_q not in main_questions_set:
                    main_questions_set.add(main_q)
                    break
            
            sub_questions = []
            sub_questions_set = set()  # 用于查重支线问题
            
            # 为当前主干问题生成支线问题
            for j in range(num_sub_questions):
                sub_prompt = f"""基于以下主干问题：
                {main_q}
                
                请生成一个相关的支线问题，这个问题应该：
                1. 与主干问题密切相关
                2. 能够深入探讨主干问题的某个具体方面
                3. 不同于已有的支线问题
                
                已有的支线问题：
                {sub_questions}
                
                请直接输出问题，不需要任何前缀。"""
                
                while True:
                    sub_q = qa_chain.run(sub_prompt).strip()
                    # 去除可能的序号和多余标点
                    sub_q = re.sub(r'^[\d\.\s、]+', '', sub_q)
                    sub_q = re.sub(r'[?？]+$', '？', sub_q)
                    
                    if sub_q not in sub_questions_set:
                        sub_questions_set.add(sub_q)
                        sub_questions.append(sub_q)
                        break
            
            questions_data.append({
                'main_question': main_q,
                'sub_questions': sub_questions
            })
            
            print(f"已生成第 {i+1} 个主干问题及其支线问题")
        
        # 转换为DataFrame格式
        rows = []
        for item in questions_data:
            main_q = item['main_question']
            for sub_q in item['sub_questions']:
                rows.append({
                    'main_question': main_q,
                    'sub_question': sub_q
                })
        
        df = pd.DataFrame(rows)
        
        # 保存文件
        if output_format == 'xlsx':
            df.to_excel('generated_questions.xlsx', index=False)
        elif output_format == 'csv':
            df.to_csv('generated_questions.csv', index=False, encoding='utf-8-sig')
        elif output_format == 'json':
            import json
            with open('generated_questions.json', 'w', encoding='utf-8') as f:
                json.dump(questions_data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    rag = DocumentRAG(openai_api_key="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")
    rag.load_pdf(r"D:\Scientific_Research\Education_Agent_Design\课程大纲&教案&逐字稿&习题.pdf")
    rag.generate_questions(num_main_questions=5, num_sub_questions=3, output_format='xlsx')

