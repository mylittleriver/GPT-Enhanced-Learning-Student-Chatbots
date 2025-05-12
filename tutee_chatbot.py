import html
import time
import tiktoken
import re
import random
import openai
import base64
import json
import streamlit as st
from streamlit_modal import Modal
from streamlit_lottie import st_lottie
import sqlite3
from db_connection import db
from util import generate_id,generate_time
import requests
from flask import Flask, request
from streamlit_cookies_controller import CookieController, RemoveEmptyElementContainer
import os
from dotenv import load_dotenv

def decrypt_uid(encrypted_uid: str, key: str) -> str:
    if encrypted_uid:
        decoded_bytes = base64.urlsafe_b64decode(encrypted_uid.encode())
        decoded_str = decoded_bytes.decode()
        decrypted_chars = [chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(decoded_str)]
        return ''.join(decrypted_chars)
    
controller = CookieController()
RemoveEmptyElementContainer()

cookie_uid = controller.get('secrectID')
cookie_cid = controller.get('course_id')

load_dotenv()

key = 'mysecretkey'
if cookie_uid:
    uid = decrypt_uid(cookie_uid, key)
    if 'course_id' not in st.session_state:
        st.session_state['course_id'] = cookie_cid

    course_id=st.session_state['course_id']
    staff=[user.strip() for user in os.getenv('ADMIN_LIST', '').split(',') if user.strip()]

    if course_id[0]:
        # cursor.execute("""
        #     SELECT course_department, course_name, course_description, course_prompt
        #     FROM courses
        #     WHERE course_id = ?
        # """, (course_id,))
        # course_data = cursor.fetchone()
        course_data = db.courses.find_one({"course_id": course_id})
        teacher_id = course_data.get('teacher_id', '')
    else:
        st.error("Course ID not found!")
        st.page_link(os.getenv("GEL_HTTP_URL"), label="Go Back to Home", icon="🏠")
        st.stop() 

    if 'generate_question' not in st.session_state:
        st.session_state['generate_question']=False

    if 'generate_random' not in st.session_state:
        st.session_state['generate_random']=False

    if 'topic_not_inserted_tutee' not in st.session_state:
        st.session_state['topic_not_inserted_tutee']=True

    if 'topic_id_tutee' not in st.session_state:
        st.session_state['topic_id_tutee'] = generate_id()

    topic_id=st.session_state['topic_id_tutee']

    encoding = tiktoken.encoding_for_model("gpt-35-turbo-0613")

    if 'admin' not in st.session_state:
        if uid in staff or uid in teacher_id:
            st.session_state['admin']=True
        else:
            st.session_state['admin']=False

    azure_key = os.getenv("AZURE_KEY")
    azure_endpoint = os.getenv("AZURE_ENDPOINT")
    azure_version = os.getenv("AZURE_VERSION")
    azure_deployment = os.getenv("AZURE_DEPLOYMENT")

    client = openai.AzureOpenAI(
        api_key=azure_key,
        api_version = azure_version,
        azure_endpoint = azure_endpoint,
        azure_deployment=azure_deployment
    )

    # if "show_modal" not in st.session_state:
    #     st.session_state["show_modal"] = False

    # def show_modal():
    #     st.session_state["show_modal"] = True

    # def hide_modal():
    #     st.session_state["show_modal"] = False

    def create_connection():
        # conn = sqlite3.connect('chatbot.db')
        conn = sqlite3.connect("/app/chatbot.db", timeout=10)  # 设置超时时间，避免锁冲突
        # conn.execute("PRAGMA journal_mode=WAL;")  # 启用 WAL 模式，允许多个进程访问
        return conn


    def insert_question(q_id, question_text, course_id):
        conn = create_connection()
        sql = '''INSERT INTO tutee_questions(q_id, q_content, course_id) VALUES(?,?, ?)'''
        cur = conn.cursor()
        cur.execute(sql, (q_id,question_text, course_id))
        conn.commit()
        cur.close()
        conn.close()


    def fetch_tutee_questions(course_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT q_content FROM tutee_questions WHERE course_id = ?", (course_id,))
        questions=[row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return questions

    def fetch_all_questions(course_id):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT q_id, q_content FROM all_questions WHERE course_id = ?", (course_id,))
        questions = cursor.fetchall()
        cursor.close()
        conn.close()
        return questions


    if "tutee_messages" not in st.session_state:
        st.session_state["tutee_messages"] = [
            
            {"role": "system", "content":''
            # '''
            #     You are a computer science student who's taking a 
            #     computer science course on Python. 
            #     You will behave like a tutee through the entire conversation.
            #     This course is an introductory course on Python programming, 
            #     which covers variables, operators, and basic control structures. 
            #     You are not sure about some problems in this course.
            #     You will be asked these questions and 
            #     you need to try to answer them. 
            #     You give wrong answers to questions.
            #     You need help from others to get the correct answer. 
            #     If asked "generate the code" or related thing, 
            #     you will generate code with error and 
            #     you will be provided with hints.
            #     You will be continuously prompted 
            #     until you get the correct answer.
            # '''
            },
            {"role": "assistant", "content":'Ask me a question to see if I am correct.'}
            

        ]



    if "random_question" not in st.session_state:
        st.session_state["random_question"] = fetch_tutee_questions(course_id)

    custom_css = """
    <style>
    .admin-label {
        color: #FF6347;
        font-weight: bold;
        font-size: 16px;
    }

    </style>
    """

    st.markdown(custom_css, unsafe_allow_html=True)

    busy_icon_css = """
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .busy-icon {
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        animation: spin 2s linear infinite;
        display: inline-block;
    }
    </style>
    """

    st.markdown(busy_icon_css, unsafe_allow_html=True)




    with st.sidebar:
        # with st.form("course_id_tutee"):
        #     cursor.execute("SELECT course_id FROM courses")
            # course_ids = [row[0] for row in cursor.fetchall()]
            # course_id = st.selectbox(
            #     "Select Course ID",
            #     course_ids
            # )
            # course_id=course_id
            # apply_changes = st.form_submit_button("Apply Changes")
        
        # if apply_changes:
        if uid in staff or uid in teacher_id:
            if st.button("Admin/Student View"):
                st.session_state['admin']=not st.session_state['admin']
        
        if course_data:
            conn = create_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM system_prompt
                WHERE course_id = ? AND chatbot_type = ?
                ORDER BY create_time DESC
                LIMIT 1;
            ''', (course_id, 'tutee'))
            latest_record = cursor.fetchone()
            cursor.close()
            conn.close()
            if latest_record and st.session_state["tutee_messages"][0]["content"]=='':
                st.session_state["tutee_messages"][0]["content"] = latest_record[0]
            else:
                course_department = course_data.get('course_department', '')
                course_name = course_data.get('course_name', '')
                course_description = course_data.get('course_description', '')
                course_prompt = course_data.get('course_prompt', '')
                # Format the course_prompt with the retrieved data
                formatted_prompt=f'''
                    You should behave like a {course_department} student who's taking a course named {course_name}. 
                    Course description: {course_description}
                    You should behave like a tutee and the user will be your tutor for this course through the entire conversation.
                    
                    You are not sure about some problems in this course.
                    You will be asked these questions and 
                    you give wrong or uncertain answers to them.
                    You need help from the user to get the correct answer. 
                    If asked "generate the code" or related thing, 
                    you will generate code with error and 
                    you will be provided with hints.
                    You will be continuously prompted 
                    until you get the correct answer and the user says you are correct.
                '''
                if st.session_state["tutee_messages"][0]["content"]=='':
                    st.session_state["tutee_messages"][0]["content"] = formatted_prompt
            st.write(f"Course ID: {course_id}")
            # st.sidebar.success("Course prompt updated successfully!")
        
        
        # teacher_id = course_data.get('teacher_id', '')
        # if uid in staff or uid in teacher_id:
        if st.session_state['admin']:
            st.markdown('<label class="admin-label">Enter new System Prompt</label>', unsafe_allow_html=True)
            @st.dialog("Update System Prompt")
            def update_system_prompt():
                new_system_prompt = st.text_area("New Prompt:", st.session_state["tutee_messages"][0]["content"], height=200)
                submitted_curr= st.button("Save for this session")
                if submitted_curr:
                    st.session_state["tutee_messages"][0]["content"] = new_system_prompt
                    st.success("System prompt updated successfully!")
                    st.rerun()

                    
                submitted_db= st.button("Save for all sessions")
                if submitted_db:
                    st.session_state["tutee_messages"][0]["content"] = new_system_prompt
                    conn = create_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO system_prompt (prompt,course_id, uid, chatbot_type)
                        VALUES (?, ?, ?, ?)
                    ''', (new_system_prompt,course_id, uid, 'tutee'))
                    conn.commit()
                    cursor.close()
                    conn.close()

                    st.success("System prompt updated successfully!")
                    st.rerun()



            if st.button("Update System Prompt"):
                update_system_prompt()  
        # if uid in staff or uid in teacher_id:
        if st.session_state['admin']:
            with st.form("add_question"):
                st.markdown('<label class="admin-label">Add New Tutee Question</label>', unsafe_allow_html=True)
                questions=fetch_all_questions(course_id)
                question_dict = {q_content: q_id for q_id, q_content in questions}

                select_question = st.selectbox(
                    "Select Question From All Questions",
                    list(question_dict.keys())  
                )
                
                add_question = st.form_submit_button("Add Selected Question")   
                if add_question:
                    if select_question:
                        q_id = question_dict[select_question]
                        insert_question(q_id, select_question, course_id)
                        st.sidebar.success("Question added successfully!")
                    else:
                        st.sidebar.warning("Please enter a question.")

                input_question = st.text_input("New Question:")
                add_question = st.form_submit_button("Add Custom Question")

                if add_question:
                    if input_question:
                        insert_question(generate_id(), input_question, course_id)
                        st.sidebar.success("Question added successfully!")
                    else:
                        st.sidebar.warning("Please enter a question.")
                
        with st.form("select tutee question"):
            questions=fetch_tutee_questions(course_id)
            select_question = st.selectbox(
                    "Select Tutee Question",
                    questions
            )
            generate_question = st.form_submit_button("Generate Question",help='ask a question for the tutee chatbot to answer')
            if select_question:
                if generate_question:
                    conn = create_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT * FROM system_prompt
                        WHERE course_id = ? AND chatbot_type = ?
                        ORDER BY create_time DESC
                        LIMIT 1;
                    ''', (course_id, 'tutee'))
                    latest_record = cursor.fetchone()
                    cursor.close()
                    conn.close()
                    # st.write("latest_record",latest_record)
                    if latest_record:
                        st.session_state["tutee_messages"] = [
                            {"role": "system", "content":latest_record[0]}
                        ]
                    st.session_state["tutee_messages"].append({"role": "user", "content": select_question})
                    if st.session_state['topic_not_inserted_tutee']:
                        db.topics.insert_one(
                            {
                                "topic_id": st.session_state['topic_id_tutee'],
                                "user_id": uid,
                                "course_id": course_id,
                                "latest_gpt_ver": os.getenv("AZURE_OPENAI_LATEST_GPT_VERSION"),
                                "chat_title": 'general',
                                "chatbot_type": "tutee"
                            }
                        )
                    total_token_count = sum(len(encoding.encode(message["content"])) for message in st.session_state["tutee_messages"])
                    user_record = db.users.find_one({"user_id": uid})
                    if user_record:
                        tokens_used = user_record.get("tokens_used")  
                        tokens_available = user_record.get("tokens_available") 
                        tokens_left=tokens_available-tokens_used
                    else:
                        st.write(f"No user record found with user_id: {uid}")
                    if total_token_count>tokens_left:
                        st.error("Quota for this course has been exceeded.")
                    else:
                        # placeholder = st.empty()
                        # placeholder.markdown('<div class="busy-icon"></div>', unsafe_allow_html=True)
                        st.session_state['generate_question']=select_question
                        
        generate_random=st.button("Generate Random Question",help='ask a random question from the list for the tutee chatbot to answer')            
        if st.session_state['random_question']:
            if generate_random:
                conn = create_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM system_prompt
                    WHERE course_id = ? AND chatbot_type = ?
                    ORDER BY create_time DESC
                    LIMIT 1;
                ''', (course_id, 'tutee'))
                latest_record = cursor.fetchone()
                cursor.close()
                conn.close()

                if latest_record:
                
                    st.session_state["tutee_messages"] = [
                        {"role": "system", "content":latest_record[0]
                    #     '''
                    #     You are a computer science student who's taking a 
                    #     computer science course on Python. 
                    #     You will behave like a tutee through the entire conversation.
                    #     This course is an introductory course on Python programming, 
                    #     which covers variables, operators, and basic control structures. 
                    #     You are not sure about some problems in this course.
                    #     You will be asked these questions and 
                    #     you need to try to answer them. 
                    #     You give wrong answers to questions.
                    #     You need help from others to get the correct answer. 
                    #     If asked "generate the code" or related thing, 
                    #     you will generate code with error and 
                    #     you will be provided with hints.
                    #     You will be continuously prompted 
                    #     until you get the correct answer.
                     #     '''
                        }
                    ]
                i=random.randint(0,len(st.session_state["random_question"])-1)
                random_question=st.session_state["random_question"][i]
                st.session_state["tutee_messages"].append({"role": "user", "content": random_question})
                if st.session_state['topic_not_inserted_tutee']:
                    db.topics.insert_one(
                        {
                            "topic_id": st.session_state['topic_id_tutee'],
                            "user_id": uid,
                            "course_id": course_id,
                            "latest_gpt_ver": os.getenv("AZURE_OPENAI_LATEST_GPT_VERSION"),
                            "chat_title": 'general',
                            "chatbot_type": "tutee"
                        }
                    )
                    st.session_state['topic_not_inserted_tutee']=False
                total_token_count = sum(len(encoding.encode(message["content"])) for message in st.session_state["tutee_messages"])
                user_record = db.users.find_one({"user_id": uid})
                if user_record:
                    tokens_used = user_record.get("tokens_used")  
                    tokens_available = user_record.get("tokens_available") 
                    tokens_left=tokens_available-tokens_used
                else:
                    st.write(f"No user record found with user_id: {uid}")
                if total_token_count>tokens_left:
                    st.error("Quota for this course has been exceeded.")
                else:
                    # placeholder = st.empty()
                    # placeholder.markdown('<div class="busy-icon"></div>', unsafe_allow_html=True)
                    st.session_state['generate_random']=select_question
                    
        st.write("Disclaimer: This chatbot is provided for educational purposes only. Logs of your chat sessions will be saved and reviewed by the teaching team to improve the course content and chatbot experience.")
        st.write("Support: If you encounter any issues or have any feedback, please reach out to the team via email at: gel.support@cityu.edu.hk.")


    block_latex_pattern = re.compile(r"\\\[(.*?)\\\]", re.DOTALL)  # 块级公式 `\[ ... \]`
    inline_latex_pattern = re.compile(r"\\\((.*?)\\\)|(?<!\\)\$(.*?)\$(?!\s*})")  # 行内公式 `\( ... \)` 和 `$...$`

    def replace_inline_latex(text):
        return inline_latex_pattern.sub(lambda m: f"${m.group(1) or m.group(2)}$", text)

    def parse_message(content):
        elements = []
        last_pos = 0

        # 解析块级公式
        for match in block_latex_pattern.finditer(content):
            start, end = match.span()
            text_before = content[last_pos:start].strip()
            latex_code = match.group(1).strip()
            
            if text_before:
                elements.append(("text", replace_inline_latex(text_before)))  # 处理行内公式
            elements.append(("latex", latex_code))  # 添加 LaTeX 公式
            last_pos = end

        # 处理剩余部分
        remaining_text = content[last_pos:].strip() if last_pos < len(content) else ""
        if remaining_text:
            formatted_text = replace_inline_latex(remaining_text)
            elements.append(("markdown", formatted_text))

        return elements

    def render_message(content):
        elements = parse_message(content)
        for elem_type, elem_content in elements:
            if elem_type == "latex":
                st.latex(rf"""{elem_content}""")  # 直接渲染 LaTeX 公式
            elif elem_type == "markdown":
                st.markdown(elem_content, unsafe_allow_html=True)  # 解析行内公式
            else:
                st.write(elem_content)


    for msg in st.session_state.tutee_messages:
        # if msg["role"] == "system":
        #     st.chat_message("system").write(msg["content"])
        if msg["role"] == "assistant":
            with st.chat_message("assistant"):
                render_message(msg["content"]) 
        elif msg["role"] == "user":
            st.chat_message("user").write(msg["content"])

    def render_streamed_text(text, placeholder):
        elements = []
        last_pos = 0

        # 处理块级公式
        for match in block_latex_pattern.finditer(text):
            start, end = match.span()
            text_before = text[last_pos:start].strip()
            latex_code = match.group(1).strip()

            if text_before:
                elements.append(("text", replace_inline_latex(text_before)))  # 处理行内公式
            elements.append(("latex", latex_code))  # 块级公式
            last_pos = end

        # 处理剩余部分（包括行内公式）
        remaining_text = text[last_pos:].strip() if last_pos < len(text) else ""
        if remaining_text:
            formatted_text = replace_inline_latex(remaining_text)  # 处理行内公式
            elements.append(("markdown", formatted_text))

        # **流式渲染**
        with placeholder.chat_message("assistant"):
            for elem_type, elem_content in elements:
                if elem_type == "latex":
                    st.latex(rf"""{elem_content}""")  # 块级公式
                elif elem_type == "markdown":
                    st.markdown(elem_content, unsafe_allow_html=True)  # 行内公式
                else:
                    st.write(elem_content)

    if st.session_state['generate_question']:
        prmp=[]
        question=st.session_state['generate_question']
        prmp.append({"role": "user", "content": question})
        response = client.chat.completions.create(
            # model="gpt-35-turbo-0613", 
            model=os.getenv("AZURE_OPENAI_LATEST_GPT_VERSION"),
            messages=prmp,
            stream=True    
        )
        messages = []
        placeholder = st.empty()
        placeholder.markdown('<div class="busy-icon"></div>', unsafe_allow_html=True)

        for chunk in response:
                if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    messages.append(chunk.choices[0].delta.content)  # 累积 GPT 输出
                    render_streamed_text(''.join(messages), placeholder) 

        assistant_msg = ''.join(messages)
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens = encoding.encode(assistant_msg)
        completion_tokens = len(tokens)
        st.session_state["tutee_messages"].append({"role": "assistant", "content": assistant_msg})
        db.chats.insert_one(
            {
                "chat_id": generate_id() + str(len(st.session_state["tutee_messages"])-1).zfill(2),
                "topic_id": topic_id,
                "time": generate_time(),
                "content": question,
                "role": "user",
                "no_of_tokens": 0,
                # "chatbot_type": "tutee"
            }
        )
        db.chats.insert_one(
            {
                "chat_id": generate_id() + str(len(st.session_state["tutee_messages"])).zfill(2),
                "topic_id": topic_id,
                "time": generate_time(),
                "content": assistant_msg,
                "role": "assistant",
                "no_of_tokens": total_token_count+ completion_tokens,
                # "chatbot_type": "tutee"
            }
        )
        db.users.update_one(
            {'user_id': uid}, 
            {'$inc': {'tokens_used': total_token_count+ completion_tokens
                    # ,'tokens_available': -(total_token_count + completion_tokens)
                    }}  
        )
        db.courses.update_one(
            {"course_id": course_id},
            {"$inc": {"tutee_questions_count": 1}},
            upsert=True  # Creates field if not exists
        )
        st.session_state['generate_question']=False
        
    if st.session_state['generate_random']:
        prmp=[]
        random_question=st.session_state['generate_random']
        prmp.append({"role": "user", "content": random_question})
        response = client.chat.completions.create(
            # model="gpt-35-turbo-0613", 
            model=os.getenv("AZURE_OPENAI_LATEST_GPT_VERSION"),
            messages=prmp,
            stream=True    
        )
        messages = []
        placeholder = st.empty()
        placeholder.markdown('<div class="busy-icon"></div>', unsafe_allow_html=True)

        for chunk in response:
                if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    messages.append(chunk.choices[0].delta.content)  # 累积 GPT 输出
                    render_streamed_text(''.join(messages), placeholder) 

        assistant_msg = ''.join(messages)
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        tokens = encoding.encode(assistant_msg)
        completion_tokens = len(tokens)
        st.session_state["tutee_messages"].append({"role": "assistant", "content": assistant_msg})
        db.chats.insert_one(
            {
                "chat_id": generate_id() + str(len(st.session_state["tutee_messages"])-1).zfill(2),
                "topic_id": topic_id,
                "time": generate_time(),
                "content": random_question,
                "role": "user",
                "no_of_tokens": 0,
                # "chatbot_type": "tutee"
            }
        )
        db.chats.insert_one(
            {
                "chat_id": generate_id() + str(len(st.session_state["tutee_messages"])).zfill(2),
                "topic_id": topic_id,
                "time": generate_time(),
                "content": assistant_msg,
                "role": "assistant",
                "no_of_tokens": total_token_count+ completion_tokens,
                # "chatbot_type": "tutee"
            }
        )
        db.users.update_one(
            {'user_id': uid}, 
            {'$inc': {'tokens_used': total_token_count+ completion_tokens
                    # ,'tokens_available': -(total_token_count + completion_tokens)
                    }}  
        )
        db.courses.update_one(
            {"course_id": course_id},
            {"$inc": {"tutee_questions_count": 1}},
            upsert=True  # Creates field if not exists
        )
        st.session_state['generate_random']=False

    prompt = st.chat_input()
    if prompt:
        st.session_state["tutee_messages"].append({"role": "user", "content": prompt})
        if st.session_state['topic_not_inserted_tutee']:
            db.topics.insert_one(
                {
                    "topic_id": st.session_state['topic_id_tutee'],
                    "user_id": uid,
                    "course_id": course_id,
                    "latest_gpt_ver": os.getenv("AZURE_OPENAI_LATEST_GPT_VERSION"),
                    "chat_title": 'general',
                    "chatbot_type": "tutee"
                }
            )
            st.session_state['topic_not_inserted_tutee']=False
        st.chat_message("user").write(prompt)
        total_token_count = sum(len(encoding.encode(message["content"])) for message in st.session_state["tutee_messages"])
        user_record = db.users.find_one({"user_id": uid})
        if user_record:
            tokens_used = user_record.get("tokens_used")  
            tokens_available = user_record.get("tokens_available") 
            tokens_left=tokens_available-tokens_used
        else:
            st.write(f"No user found with user_id: {uid}")
        if total_token_count>tokens_left:
            st.error("Quota for this course has been exceeded.")
        else:

            placeholder = st.empty()
            placeholder.markdown('<div class="busy-icon"></div>', unsafe_allow_html=True)

            response = client.chat.completions.create(
                # model="gpt-35-turbo-0613", 
                model=os.getenv("AZURE_OPENAI_LATEST_GPT_VERSION"),
                messages=st.session_state["tutee_messages"],
                stream=True    
            )
            messages = []

            for chunk in response:
                if len(chunk.choices) > 0 and chunk.choices[0].delta.content:
                    messages.append(chunk.choices[0].delta.content)  # 累积 GPT 输出
                    render_streamed_text(''.join(messages), placeholder) 
                    
            assistant_msg = ''.join(messages)
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            tokens = encoding.encode(assistant_msg)
            completion_tokens = len(tokens)
            st.session_state["tutee_messages"].append({"role": "assistant", "content": assistant_msg})
            
            # placeholder.chat_message("assistant").write(assistant_msg)
            db.chats.insert_one(
                {
                    "chat_id": generate_id() + str(len(st.session_state["tutee_messages"])-1).zfill(2),
                    "topic_id": topic_id,
                    "time": generate_time(),
                    "content": prompt,
                    "role": "user",
                    "no_of_tokens": 0,
                    # "chatbot_type": "tutee"
                }
            )
            db.chats.insert_one(
                {
                    "chat_id": generate_id() + str(len(st.session_state["tutee_messages"])).zfill(2),
                    "topic_id": topic_id,
                    "time": generate_time(),
                    "content": assistant_msg,
                    "role": "assistant",
                    "no_of_tokens": total_token_count+ completion_tokens,
                    # "chatbot_type": "tutee"
                }
            )
            db.users.update_one(
                {'user_id': uid}, 
                {'$inc': {'tokens_used': total_token_count+ completion_tokens
                    # ,'tokens_available': -(total_token_count + completion_tokens)
                    }}  
            )
            # Update tutee question count for course
            db.courses.update_one(
                {"course_id": course_id},
                {"$inc": {"tutee_questions_count": 1}},
                upsert=True  # Creates field if not exists
            )

    st.caption("Use Shift+Enter to add a new line.")
    # cursor.close()
    # conn.close()

