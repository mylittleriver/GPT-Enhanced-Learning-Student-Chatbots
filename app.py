import openai
import streamlit as st
import sqlite3
from st_pages import add_page_title
st.set_page_config(layout="wide")

pages = [
        st.Page("tutor_chatbot.py", title="Tutor Chatbot"),
        st.Page("tutee_chatbot.py", title="Tutee Chatbot"),
        st.Page("quizzer_chatbot.py", title="Quizzer Chatbot")
    ]

pg = st.navigation(pages)
add_page_title(pg)
pg.run()
