#import libraries

from dotenv import load_dotenv
load_dotenv() ## loading environment variables

import os
import streamlit as st
import google.generativeai as genai

genai.configure(api_key= os.getenv("GOOGLE_API_KEY")) ## configure google api 

## function to load gemini pro model and get responses
model = genai.GenerativeModel("gemini-1.5-flash")

def get_gemini_response(question):
    response = model.generate_content(question)
    return response.text

## intialise stream lit app

st.set_page_config(page_title="Queries and Ans")
st.header("Chat-Application")
input = st.text_input("Input: ", key="input")

submit = st.button("give me an answer")


## when submit is clicked
if submit:
    response = get_gemini_response(input)
    st.subheader("The Answer is")
    st.write(response)