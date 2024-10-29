# AI_Education
Shaping the Future of Learning

设计一个多智能体的Problem-Based Learning (PBL) 教育系统。系统的目标是通过对话式交互，帮助用户掌握数据库中的一系列知识点，并实现自动化的学习过程评估与反馈。


## About DataBase
Currently using a MySQL database, the table is t1.
```sql
-- auto-generated definition
create table t1
(
    id                  int(10) auto_increment
        primary key,
    course_name         varchar(20)          null,
    question            varchar(100)         null,
    content_correlation varchar(20)          null,
    question_depth      varchar(20)          null,
    learning_process    varchar(20)          null,
    learner_tag         tinyint(1) default 0 null,
    answer              varchar(1000)        null
);
```

### Field Descriptions

- `course_name`:课程名称，表示该条数据对应的课程
- `question`:问题文本，包含待回答的问题内容
- `content_correlation`:内容相关性，字段值可选如下四种：
    - 背景知识：提供背景信息
    - 核心内容：与主题直接相关的主要信息
    - 主要内容：关键点和主题的主要内容
    - 延伸内容：拓展性的信息，包含附加知识
- `question_depth`:问题深度，字段值可选如下六种：
    - 基础问题：基础知识问题
    - 理解问题：测试理解能力的问题
    - 应用问题：应用知识于实际问题的问题
    - 分析问题：分析与解构信息的问题
    - 评估问题：对信息进行评估的问题
    - 综合问题：综合多方面知识的问题
- `learning_process`:学习进度，字段值可选如下六种：
    - 入门阶段：初学者阶段
    - 深化阶段：知识深化阶段
    - 应用阶段：知识应用阶段
    - 综合阶段：综合知识运用阶段
    - 拓展阶段：拓展与深入学习阶段
    - 独立：独立掌握知识的阶段
- `learner_tag`:学习者标签，标识学习者的状态（默认为0），表示学习者还没有学会这道题目
- `answer`:答案字段，应包含从该文本中提取出的正确回答



