##load the enviroment
from dotenv import load_dotenv
load_dotenv()


##import all necessary Modules
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image


genai.configure(api_key= os.getenv("GOOGLE_API_KEY")) ## configure google api 


## intialise model

model  = genai.GenerativeModel('gemini-1.5-pro')

def get_gemini_response(input, img, prompt):
    response = model.generate_content([input, img[0], prompt])
    return response.text

def input_image_details(uploaded_file):
    if uploaded_file is not None:
        ## Read the file into bytes
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type" : uploaded_file.type,
                "data" : bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")



##Intialise streamlit app

st.set_page_config(page_title = "Invoice Queries")
st.header("Multi language Invoice Extractor")
input = st.text_input("Input Prompt:" , key="input")
uploaded_file = st.file_uploader("choose an Image", type=['jpg','jpeg','png'])
img = ""

if uploaded_file is not None:
    img = Image.open(uploaded_file)
    st.image(img, caption = "uplaoded image", use_column_width=True)
submit = st.button("Tell me about Invoice")
input_Prompt = """
you are an expert in understanding invoices, we will upload a image as invoices 
and you will have to answer any questions based on invoice uploaded
"""
if submit:
    img_data = input_image_details(uploaded_file)
    response = get_gemini_response(input_Prompt, img_data,input)
    st.subheader("The Response is")
    st.write(response)