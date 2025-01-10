import cProfile
from functools import lru_cache
import pstats
from io import StringIO
import html
import time
import tiktoken
import re
import openai
import base64
import json
import streamlit as st
from streamlit_modal import Modal

import sqlite3
from db_connection import db
from util import generate_id,generate_time
import requests
from flask import Flask, request
from streamlit_cookies_controller import CookieController, RemoveEmptyElementContainer
import os



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

# st.write("secrectID: ",cookie_uid)


key = 'mysecretkey'
if cookie_uid:
    uid = decrypt_uid(cookie_uid, key)

    if 'uid' not in st.session_state: 
        st.session_state['uid'] = uid
    if 'course_id' not in st.session_state:
        st.session_state['course_id'] = cookie_cid

    course_id = st.session_state['course_id']


    if course_id[0]:

        course_data = db.courses.find_one({"course_id": course_id})
        teacher_id = course_data.get('teacher_id', '')
    else:
        st.error("Course ID not found!")
        st.page_link("https://gel-student.cs.cityu.edu.hk/", label="Go Back to Home", icon="🏠")
        st.stop() 

    

    if 'topic_not_inserted_tutor' not in st.session_state:
        st.session_state['topic_not_inserted_tutor'] = True

    if 'topic_id_tutor' not in st.session_state:
        st.session_state['topic_id_tutor'] = generate_id()
        
    if 'similarity_threshold' not in st.session_state:
        st.session_state['similarity_threshold']=70

    if 'correctness_threshold1' not in st.session_state:
        st.session_state['correctness_threshold1']=50

    if 'correctness_threshold2' not in st.session_state:
        st.session_state['correctness_threshold2']=75

    topic_id = st.session_state['topic_id_tutor']

    staff=['manhlai','abchan','shujunxia2']

    if 'admin' not in st.session_state:
        if uid in staff or uid in teacher_id:
            st.session_state['admin']=True
        else:
            st.session_state['admin']=False

    # Azure API credentials
    azure_key = "c42959fcc37648f0bdee8ed85f0ea6ea"
    azure_endpoint = "https://abchan-fite-gpt.openai.azure.com/"
    azure_version = "2023-07-01-preview"

    client = openai.AzureOpenAI(
        api_key=azure_key,
        api_version=azure_version,
        azure_endpoint=azure_endpoint
    )


    def create_connection():
        conn = sqlite3.connect('chatbot.db')
        return conn

    conn = create_connection()
    cursor = conn.cursor()

    if 'correctness_api' not in st.session_state:
        cursor.execute('''
            SELECT * FROM correctness_api
            WHERE course_id = ? 

        ''', (course_id,))
        record = cursor.fetchall()
        record = record[0] if record else None
        if record[1] == 1:
            st.session_state['correctness_api']=True  
        else:
            st.session_state['correctness_api']=False

    def update_correctness_api(is_active):

        cursor.execute("UPDATE correctness_api SET is_active = ? WHERE course_id = ?", (is_active, course_id))
        conn.commit()
        cursor.close()
        conn.close()

    # Initialize session state for tutor messages
    if "tutor_messages" not in st.session_state:
        st.session_state["tutor_messages"] = [
            {"role": "system", "content":''
                # '''
                # You are a tutor that helps students 
                # to answer questions about a 
                # computer science course on Python programming. 
                # This course is an introductory course 
                # on Python programming, which covers 
                # variables, operators, and basic control structures. 
                # You are friendly and concise. 
                # You should not be an answering machine 
                # that simply spits out the solution, 
                # but a “questioning” machine 
                # that guides and inspires the student to 
                # develop their own understanding.  
                # You do not provide answers that are not 
                # related to Python programming.
                # Instead of giving away the answer, 
                # you prefer to give students hints 
                # by asking “what if” questions.
                # You need to pay attention to 
                # the frequently asked questions that 
                # are asked by other students.
                # '''
                
            },
            {"role": "assistant", "content": "I'm your tutor in this course. How can I help you?"}

        ]

    

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
    if 'correctness_score' not in st.session_state:
        st.session_state['correctness_score']=0

    if 'similar' not in st.session_state:
        st.session_state['similar']=False

    def determine_correctness(score,threshold1,threshold2):
        if score < threshold1:
            # return "probably incorrect"
            return "❌"
        elif score < threshold2:
            # return "probably correct"
            return "🤔"
        else:
            # return "definitely correct"
            return "✔"

    # Sidebar - Course selection and system prompt update
    with st.sidebar:
        if uid in staff or uid in teacher_id:
            if st.button("Admin/Student View"):
                st.session_state['admin']=not st.session_state['admin']
        if course_data:
            cursor.execute('''
                SELECT * FROM system_prompt
                WHERE course_id = ? AND chatbot_type = ?
                ORDER BY create_time DESC
                LIMIT 1;
            ''', (course_id, 'tutor'))
            latest_record = cursor.fetchone()

            if latest_record and st.session_state["tutor_messages"][0]["content"]=='':
                st.session_state["tutor_messages"][0]["content"] = latest_record[0]
            else:
                course_department = course_data.get('course_department', '')
                course_name = course_data.get('course_name', '')
                course_description = course_data.get('course_description', '')
                course_prompt = course_data.get('course_prompt', '')
                formatted_prompt = course_prompt.replace('<course_department>', course_department) \
                                                .replace('<course_name>', course_name) \
                                                .replace('<course_description>', course_description)
                if st.session_state["tutor_messages"][0]["content"]=='':
                    st.session_state["tutor_messages"][0]["content"] = f'''
                        {formatted_prompt} 
                        You should not be an answering machine that simply spits out the solution, 
                        but a “questioning” machine that guides and inspires the student to 
                        develop their own understanding. Instead of giving away the answer, 
                        you prefer to give students hints by asking “what if” questions.
                        You need to pay attention to the frequently asked questions that 
                        are asked by other students.
                    '''
            st.write(f"Course ID: {course_id}")

        if st.session_state['admin']:
            st.markdown('<label class="admin-label">Enter new System Prompt</label>', unsafe_allow_html=True)
            @st.dialog("Update System Prompt")
            def update_system_prompt():
                new_system_prompt = st.text_area("New Prompt:", st.session_state["tutor_messages"][0]["content"], height=200)
                submitted_curr= st.button("Save for this session")
                if submitted_curr:
                    st.session_state["tutor_messages"][0]["content"] = new_system_prompt
                    st.success("System prompt updated successfully!")
                    st.rerun()

                    
                submitted_db= st.button("Save for all sessions")
                if submitted_db:
                    st.session_state["tutor_messages"][0]["content"] = new_system_prompt
                    conn = create_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO system_prompt (prompt,course_id, uid, chatbot_type)
                        VALUES (?, ?, ?, ?)
                    ''', (new_system_prompt,course_id, uid, 'tutor'))
                    conn.commit()
                    st.success("System prompt updated successfully!")
                    st.rerun()

            if st.button("Update System Prompt"):
                update_system_prompt() 
        if st.session_state['admin']:
            if st.button("Toggle Student Correctness API Access"):
                st.session_state['correctness_api']=not st.session_state['correctness_api']
                if st.session_state['correctness_api']==True:
                    update_correctness_api(1)
                else:
                    update_correctness_api(0)
            st.write("Current Correctness API Access:",st.session_state['correctness_api'])
                    

                
            

        # st.write('Hint: Low correctness score means the chatbot has difficulty answering this question. You can flag the current answer as incorrect by clicking the "flag as incorrect" button below and ask this question again in Tutee Chatbot.')
        flagged=st.button("flag as incorrect❌",help="flag the current answer as incorrect")
        if flagged and st.session_state["similar"]==False:
            # Store the current question into the all_questions table
            if st.session_state["tutor_messages"] and st.session_state["correctness_score"]:
                last_user_msg = next(
                    (msg["content"] for msg in reversed(st.session_state["tutor_messages"]) if msg["role"] == "user"), None)
                if last_user_msg:
                    cursor.execute("""
                        INSERT INTO all_questions (q_id, assessment, q_content, correctness_score, course_id,similarity_threshold, correctness_threshold_low, correctness_threshold_high)
                        VALUES (?, ?, ?,?, ?, ?, ?, ?)
                    """, (generate_id(), 'N/A',last_user_msg, st.session_state["correctness_score"], course_id, st.session_state['similarity_threshold'], st.session_state['correctness_threshold1'], st.session_state['correctness_threshold2']))
                    conn.commit()
                    st.sidebar.success("Question saved to all_questions.")

        
        
        if st.session_state['admin']:
            similar_threshold = st.slider("Set similarity threshold:", min_value=0, max_value=100, value=70)
            correctness_threshold1 = st.sidebar.slider("Set threshold for 'probably incorrect'❌ and 'probably correct'🤔:", min_value=0, max_value=99, value=50,help='set upper threshold for "probably incorrect" and lower threshold for "probably correct"')
            correctness_threshold2 = st.sidebar.slider("Set threshold for 'probably correct'🤔 and 'definitely correct'✔:", min_value=correctness_threshold1+1, max_value=100, value=75,help='set upper threshold for "probaby correct" and lower threshold for "definitely correct"')
            st.session_state['similarity_threshold']=similar_threshold
            st.session_state['correctness_threshold1']=correctness_threshold1
            st.session_state['correctness_threshold2']=correctness_threshold2   
        
        # uid=st.session_state['uid']
        # with st.form("system_prompt_tutor"):
        #     st.markdown('<label class="admin-label">Enter new System Prompt</label>', unsafe_allow_html=True)
        #     new_system_prompt = st.text_area("New Prompt:", st.session_state["tutor_messages"][0]["content"])
        #     update_system_prompt = st.form_submit_button("Update System Prompt")

        #     if update_system_prompt:
        #         st.session_state["tutor_messages"][0]["content"] = new_system_prompt
        #         st.sidebar.success("System prompt updated successfully!")
        st.write("Disclaimer: This chatbot is provided for educational purposes only. Logs of your chat sessions will be saved and reviewed by the teaching team to improve the course content and chatbot experience.")
        st.write("Support: If you encounter any issues or have any feedback, please reach out to the team via email at: gel.support@cityu.edu.hk.")

    # if st.session_state['admin']:
    #     st.subheader("Usage Dashboard")
        # chats_collection = db['chats']
        # topics_collection = db['topics']
        # users_collection = db['users']

        # def get_chat_data(period_days):
        #     current_time_ms = int(time.time() * 1000)
        #     period_ms = period_days * 24 * 60 * 60 * 1000
        #     period_ago_ms = current_time_ms - period_ms

        #     query = {
        #         "role": "user",
        #         "time": {"$gte": str(period_ago_ms)}
        #     }

        #     recent_user_chats = list(chats_collection.find(query))

        #     user_ids = set()
        #     session_counts = {}

        #     for chat in recent_user_chats:
        #         topic_id = chat['topic_id']
        #         topic = topics_collection.find_one({"topic_id": topic_id})
        #         if topic:
        #             user_id = users_collection.find_one({"user_id": topic['user_id']})
        #             if user_id:
        #                 user_ids.add(user_id['user_id'])
        #                 session_counts[user_id['user_id']] = session_counts.get(user_id['user_id'], 0) + 1

        #     return len(user_ids), sum(session_counts.values())

    #     days = st.number_input("Enter the number of days", min_value=1, max_value=365, value=30, step=1)

    #     unique_users, total_sessions = get_chat_data(days)

    #     st.write(f"Number of unique users in the last {days} days: {unique_users}")
    #     st.write(f"Number of total sessions in the last {days} days: {total_sessions}")

    #     import plotly.graph_objects as go

    #     fig = go.Figure(data=[
    #         go.Bar(name='Users', x=['Users'], y=[unique_users]),
    #         go.Bar(name='Sessions', x=['Sessions'], y=[total_sessions])
    #     ])

    #     fig.update_layout(
    #         title=f"Usage Dashboard - Users and Sessions for the Last {days} Days",
    #         barmode='group',
    #         xaxis_title="Metrics",
    #         yaxis_title="Count"
    #     )

    #     st.plotly_chart(fig)

    # Chat interface
    for msg in st.session_state["tutor_messages"]:
        # if msg["role"] == "system":
        #     st.chat_message("system").write(msg["content"])
        if msg["role"] == "assistant":
            st.chat_message("assistant").write(msg["content"])
        elif msg["role"] == "user":
            st.chat_message("user").write(msg["content"])


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


    @lru_cache(maxsize=128)
    def cached_simi_response(prompt):
        simi_prompt = prompt
        # simi_url = "http://144.214.37.18:8091/similarity"
        simi_url = "http://144.214.37.18:8092/similarity"
        data = {
            "course_id": course_id,
            "assessment": [],
            "prompt": simi_prompt
        }
        response = requests.post(simi_url, headers={"Content-Type": "application/json"}, json=data)
        return response


    def get_gpt_response(messages):
        response = client.chat.completions.create(
            model="gpt-35-turbo-0613",
            messages=messages,
            stream=True       
        )
        return response
    # @lru_cache(maxsize=128)
    # def get_gpt_response_cached(messages):
    #     response = client.chat.completions.create(
    #         model="gpt-35-turbo-0613",
    #         messages=tuple(messages),  # 转换为可哈希类型
    #         stream=True       
    #     )
    #     return response

    def get_correctness_response(prompt,assistant_msg):
        # correctness_url = "http://144.214.37.18:8070/correctness"
        correctness_url = "http://144.214.37.18:8078/correctness"
        data = {
            "question": prompt,
            "answer": assistant_msg
        }
        response = requests.post(correctness_url, headers={
            "Content-Type": "application/json",
            "Authorization": "9aa0864a-467f-4434-9e19-89fc2f07f04a"
        }, json=data)
        return response
    # try:
    #     # start_time = time.time()
    #     response = requests.post(simi_url, headers={"Content-Type": "application/json"}, json=data)
    #     # end_time = time.time()

    #     # elapsed_time = end_time - start_time
    #     # if st.session_state['admin']:
    #     #     st.markdown("⌛",help=f"Similarity response generation took {elapsed_time:.2f} seconds")
        
    #     if response.status_code == 200:
    #         json=response.json()
    #         formatted_results = [
    #             f"(similarity score: {result['confidence_score']:.2f}, question id: {result['question_id']})"
    #             for result in json["results"] if result is not None
    #         ]
    #         result_line = ", ".join(formatted_results)
    #         if st.session_state['admin']:
    #             with st.expander("Show similarity results"):
    #                 st.write(result_line)
    #         if any(result is not None and result["confidence_score"] > st.session_state['similarity_threshold'] for result in json["results"]):
    #             st.session_state['similar'] = True               
    #             placeholder.chat_message("assistant").write("There is an assignment question similar to this, so I am refusing to answer.")
                
    #     elif response.status_code == 404:
    #         st.write("Error: 404 Not Found!")
    #     elif response.status_code == 500:
    #         st.write("Error: Internal Server Failed!")
    #     else:
    #         st.write(f"Error: {response.status_code}!")

    # except requests.exceptions.RequestException as e:
    #     st.write("Error: Request failed!")
    def generate_all_responses(prompt):
        simi_prompt=prompt        
        try:
            simi_response=cached_simi_response(simi_prompt)

            if simi_response.status_code == 200:
                json=simi_response.json()
                formatted_results = [
                    f"(similarity score: {result['confidence_score']:.2f}, question id: {result['question_id']})"
                    for result in json["results"] if result is not None
                ]
                result_line = ", ".join(formatted_results)
                if st.session_state['admin']:
                    with st.expander("Show similarity results"):
                        st.write(result_line)
                if any(result is not None and result["confidence_score"] > st.session_state['similarity_threshold'] for result in json["results"]):
                    st.session_state['similar'] = True               
                    placeholder.chat_message("assistant").write("There is an assignment question similar to this, so I am refusing to answer.")
                    
            elif simi_response.status_code == 404:
                st.write("Error: 404 Not Found!")
            elif simi_response.status_code == 500:
                st.write("Error: Internal Server Failed!")
            else:
                st.write(f"Error: {simi_response.status_code}!")
        except requests.exceptions.RequestException as e:
            st.write("Error: Request failed!") 
        
        if not st.session_state['similar']:
            messages=st.session_state["tutor_messages"]
            gpt_response=get_gpt_response(messages)
            # start_time = time.time()

            # response = client.chat.completions.create(
            #     model="gpt-35-turbo-0613",
            #     messages=st.session_state["tutor_messages"],
            #     stream=True       
            # )
            # end_time = time.time()

            # elapsed_time = end_time - start_time
            # if st.session_state['admin']:
            #     st.markdown("⌛",help=f"GPT response generation took {elapsed_time:.2f} seconds")
            messages = []

            for chunk in gpt_response:  # Iterate over the stream
                if len(chunk.choices) > 0:
                    if chunk.choices[0].delta.content:
                        messages.append(chunk.choices[0].delta.content)
                        placeholder.chat_message("assistant").write(''.join(messages))
            assistant_msg = ''.join(messages)
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            tokens = encoding.encode(assistant_msg)
            completion_tokens = len(tokens)
            st.session_state["tutor_messages"].append({"role": "assistant", "content": assistant_msg})                
            db.chats.insert_one(
                {
                    "chat_id": generate_id() + str(len(st.session_state["tutor_messages"])-1).zfill(2),
                    "topic_id": topic_id,
                    "time": generate_time(),
                    "content": prompt,
                    "role": "user",
                    "no_of_tokens": 0,
                    # "chatbot_type": "tutor"
                }
            )
            db.chats.insert_one(
                {
                    "chat_id": generate_id() + str(len(st.session_state["tutor_messages"])).zfill(2),
                    "topic_id": topic_id,
                    "time": generate_time(),
                    "content": assistant_msg,
                    "role": "assistant",
                    "no_of_tokens": total_token_count+ completion_tokens,
                    # "chatbot_type": "tutor"
                }
            )
            db.users.update_one(
                {'user_id': uid}, 
                {'$inc': {'tokens_used': total_token_count+ completion_tokens}}  
            )
            if st.session_state['correctness_api']==True or st.session_state['admin']:
                correct_prompt=prompt           
                try:
                    correct_response=get_correctness_response(correct_prompt,assistant_msg)
                    if correct_response.status_code == 200:
                        json=correct_response.json()
                        st.session_state["correctness_score"]= json["confidence_score"]
                        correctness_score=st.session_state["correctness_score"]
                        correctness_threshold1=st.session_state['correctness_threshold1']
                        correctness_threshold2=st.session_state['correctness_threshold2']
                        st.markdown(determine_correctness(correctness_score, correctness_threshold1, correctness_threshold2),help=f"correctness score: {correctness_score:.2f} (Beta)")
                    elif correct_response.status_code == 400:
                        st.write("Error: 404 Not Found!") # question not found
                    elif correct_response.status_code == 403:
                        st.write("Error: 403 Forbidden!") # unauthorized
                    elif correct_response.status_code == 500:
                        st.write("Error: GPT generation failed!")
                    else:
                        st.write(f"Error: {correct_response.status_code}!")
                except requests.exceptions.RequestException as e:
                    st.write(f"Error: Request failed! {e}")

    # def profile_generate_all_responses(prompt):
    #     profiler = cProfile.Profile()
    #     profiler.enable()  
    #     generate_all_responses(prompt)  
    #     profiler.disable() 

    #     s = StringIO()
    #     ps = pstats.Stats(profiler, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
    #     ps.print_stats()
    #     with st.expander("Performance Profiling"):
    #         st.text(s.getvalue())

    def profile_generate_all_responses(prompt):
        profiler = cProfile.Profile()
        profiler.enable()
        generate_all_responses(prompt)
        profiler.disable()

        s = StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats(pstats.SortKey.CUMULATIVE)
        
        ps.print_stats('generate_all_responses')
        ps.print_stats('cached_simi_response')
        ps.print_stats('get_gpt_response')
        ps.print_stats('get_correctness_response')
        
        with st.expander("Performance Profiling"):
            st.text(s.getvalue())

    

    if prompt := st.chat_input():
        
        st.session_state["similar"]=False    
        st.session_state["tutor_messages"].append({"role": "user", "content": prompt})
        if st.session_state['topic_not_inserted_tutor']:
            st.write("topic not inserted")
            db.topics.insert_one(
                {
                    "topic_id": st.session_state['topic_id_tutor'],
                    "user_id": uid,
                    "course_id": course_id,
                    "latest_gpt_ver": 'gpt-35-turbo-0613',
                    "chat_title": 'general',
                    "chatbot_type": "tutor"
                }
            )
            st.write('topic_id',st.session_state['topic_id_tutor'])
            st.write("topic inserted")
            st.session_state['topic_not_inserted_tutor']=False
        st.chat_message("user").write(prompt)
        placeholder = st.empty()
        placeholder.markdown('<div class="busy-icon"></div>', unsafe_allow_html=True)     
        encoding = tiktoken.encoding_for_model("gpt-35-turbo-0613")
        total_token_count = sum(len(encoding.encode(message["content"])) for message in st.session_state["tutor_messages"])
        # token_count = len(encoding.encode(prompt))
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
            result = db.users.update_one(
                {'user_id': uid}, 
                {'$inc': {'tokens_used': total_token_count}}  
            )
            if result.matched_count == 0:
                st.write("No token record found with that user_id.")
            # generate_all_responses(prompt)
            if st.session_state['admin']:
                profile_generate_all_responses(prompt)
            else:
                generate_all_responses(prompt)

            # simi_prompt=prompt
            # try:
            #     simi_response=get_simi_response(simi_prompt)

            #     if simi_response.status_code == 200:
            #         json=simi_response.json()
            #         formatted_results = [
            #             f"(similarity score: {result['confidence_score']:.2f}, question id: {result['question_id']})"
            #             for result in json["results"] if result is not None
            #         ]
            #         result_line = ", ".join(formatted_results)
            #         if st.session_state['admin']:
            #             with st.expander("Show similarity results"):
            #                 st.write(result_line)
            #         if any(result is not None and result["confidence_score"] > st.session_state['similarity_threshold'] for result in json["results"]):
            #             st.session_state['similar'] = True               
            #             placeholder.chat_message("assistant").write("There is an assignment question similar to this, so I am refusing to answer.")
                        
            #     elif simi_response.status_code == 404:
            #         st.write("Error: 404 Not Found!")
            #     elif simi_response.status_code == 500:
            #         st.write("Error: Internal Server Failed!")
            #     else:
            #         st.write(f"Error: {simi_response.status_code}!")
            # except requests.exceptions.RequestException as e:
            #     st.write("Error: Request failed!") 
            
            # if not st.session_state['similar']:
            #     gpt_response=get_gpt_response(messages)
                # start_time = time.time()

                # response = client.chat.completions.create(
                #     model="gpt-35-turbo-0613",
                #     messages=st.session_state["tutor_messages"],
                #     stream=True       
                # )
                # end_time = time.time()

                # elapsed_time = end_time - start_time
                # if st.session_state['admin']:
                #     st.markdown("⌛",help=f"GPT response generation took {elapsed_time:.2f} seconds")
                # messages = []
                # for chunk in response:  # Iterate over the stream
                #     if len(chunk.choices) > 0:
                #         if chunk.choices[0].delta.content:
                #             messages.append(chunk.choices[0].delta.content)
                #             placeholder.chat_message("assistant").write(''.join(messages))
                # assistant_msg = ''.join(messages)
                # encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
                # tokens = encoding.encode(assistant_msg)
                # completion_tokens = len(tokens)
                # st.session_state["tutor_messages"].append({"role": "assistant", "content": assistant_msg})                db.chats.insert_one(
                #     {
                #         "chat_id": generate_id() + str(len(st.session_state["tutor_messages"])-1).zfill(2),
                #         "topic_id": topic_id,
                #         "time": generate_time(),
                #         "content": prompt,
                #         "role": "user",
                #         "no_of_tokens": 0,
                #         # "chatbot_type": "tutor"
                #     }
                # )
                # db.chats.insert_one(
                #     {
                #         "chat_id": generate_id() + str(len(st.session_state["tutor_messages"])).zfill(2),
                #         "topic_id": topic_id,
                #         "time": generate_time(),
                #         "content": assistant_msg,
                #         "role": "assistant",
                #         "no_of_tokens": total_token_count+ completion_tokens,
                #         # "chatbot_type": "tutor"
                #     }
                # )
                # db.users.update_one(
                #     {'user_id': uid}, 
                #     {'$inc': {'tokens_used': total_token_count+ completion_tokens}}  
                # )
                # if st.session_state['correctness_api']==True or st.session_state['admin']:
                    # correctness_url = "http://144.214.37.18:8070/correctness"
                    # data = {
                    #     "question": prompt,
                    #     "answer": assistant_msg
                    # }
                    # correct_prompt=prompt            
                    # try:
                        # response = requests.post(correctness_url, headers={
                        #     "Content-Type": "application/json",
                        #     "Authorization": "9aa0864a-467f-4434-9e19-89fc2f07f04a"
                        # }, json=data)
                    #     correct_response=get_correctness_response(correct_prompt)
                    #     if correct_response.status_code == 200:
                    #         json=correct_response.json()
                    #         st.session_state["correctness_score"]= json["confidence_score"]
                    #         correctness_score=st.session_state["correctness_score"]
                    #         correctness_threshold1=st.session_state['correctness_threshold1']
                    #         correctness_threshold2=st.session_state['correctness_threshold2']
                    #         st.markdown(determine_correctness(correctness_score, correctness_threshold1, correctness_threshold2),help=f"correctness score: {correctness_score:.2f} (Beta)")
                    #     elif correct_response.status_code == 400:
                    #         st.write("Error: 404 Not Found!") # question not found
                    #     elif correct_response.status_code == 403:
                    #         st.write("Error: 403 Forbidden!") # unauthorized
                    #     elif correct_response.status_code == 500:
                    #         st.write("Error: GPT generation failed!")
                    #     else:
                    #         st.write(f"Error: {correct_response.status_code}!")
                    # except requests.exceptions.RequestException as e:
                    #     st.write(f"Error: Request failed! {e}")

    st.caption("Use Shift+Enter to add a new line.")

    



    conn.close()
            

