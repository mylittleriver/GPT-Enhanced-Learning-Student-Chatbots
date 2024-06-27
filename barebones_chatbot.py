import openai
import streamlit as st
# from decouple import config

azure_key = "c42959fcc37648f0bdee8ed85f0ea6ea"
azure_endpoint = "https://abchan-fite-gpt.openai.azure.com/"
azure_version = "2023-07-01-preview"

st.title("AI Tutor Chatbot")
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "How can I help you?"},
        {"role": "system", "content": "You are a tutor that helps students to answer questions about a computer science course on Python programming. This course is an introductory course on Python programming, which covers variables, operators, and basic control structures. You are friendly and concise. You only provide factual answers to queries, and do not provide answers that are not related to Python programming."}

    ]

for msg in st.session_state.messages:
    if msg["role"] != "system":
        st.chat_message(msg["role"]).write(msg["content"])


if prompt := st.chat_input():
    
    
    client = openai.AzureOpenAI(
        api_key=azure_key,
        api_version = azure_version,
    	azure_endpoint = azure_endpoint
    )
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    response = client.chat.completions.create(model="gpt-35-turbo-0613", messages=st.session_state.messages)
    msg = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)