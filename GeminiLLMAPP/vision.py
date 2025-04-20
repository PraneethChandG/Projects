#import libraries

from dotenv import load_dotenv
load_dotenv() ## loading environment variables

import os
import streamlit as st
import google.generativeai as genai
from PIL import Image

genai.configure(api_key= os.getenv("GOOGLE_API_KEY")) ## configure google api 

## function to load gemini pro model and get responses
model = genai.GenerativeModel("gemini-2.0-flash")

def get_gemini_response(input,img):
    if not input:
        response = model.generate_content([input, img])
    else:
        response = model.generate_content(img)


    return response.text

## stream lit  app
st.set_page_config(page_title="Queries and Ans")
st.header("AI-Application")
input = st.text_input("Input: ", key="input")

uploaded_file = st.file_uploader("choose an image.. ", type = ["jpg", "jpeg", "png"])
img = ""

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption='Uploaded Image', use_container_width=True)

submit = st.button("tell me about the image")

## if submit is clicked
if submit:
    response = get_gemini_response(input, img)

    st.subheader("The Response is")
    st.write(response)