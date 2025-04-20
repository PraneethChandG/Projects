from dotenv import load_dotenv
load_dotenv()

import os
import streamlit as st
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

## write a function to load gemini model and get response

model = genai.GenerativeModel("gemini-2.0-flash-001")
chat = model.start_chat(history=[])


def get_gemini_response(question):
    response = chat.send_message(question, stream= True)
    return response

##intialise Streamlit app
st.set_page_config(page_title="Q&A")
st.header("LLM Application")

##intialise session State for chat history if it doesn't exist

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

input = st.text_input("Input :",key="input")
submit = st.button("tell me the answer")

if submit and input:
    response = get_gemini_response(input)
    ##add user query and response to session history
    st.session_state['chat_history'].append(("You", input))
    st.subheader("The Response is")
    for chunk in response:
        st.write(chunk.text)
        st.session_state['chat_history'].append(("LLM", chunk.text))

st.subheader("History")
for role,text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")
