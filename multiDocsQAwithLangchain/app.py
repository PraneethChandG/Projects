import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai

#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Chat with PDF")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)  # streamlit uploaded file acts like a file-like object
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 10000, chunk_overlap= 1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model= "models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embeddings)
    vector_store.save_local("faiss_index")
    
def get_conversational_chain():
    prompt_template = """
    Answer the question as detailed as possible from the provided context. Make sure to provide all the details. If the answer is not in 
    the provided context, just say, "answer is not available in the context." Don't provide a wrong answer.

    Context:
    {context}

    Question:
    {question}

    Answer:
    """


    model  = ChatGoogleGenerativeAI(model = "gemini-1.5-pro", temperature =0.3)

    prompt = PromptTemplate(template= prompt_template, input_variables = ["context", "question"])

    chain =load_qa_chain(model, chain_type = "stuff", prompt= prompt)
    return chain

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Load the FAISS index
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

    # Search for documents related to the question
    docs = new_db.similarity_search(user_question)

    
    # Get the conversational chain
    chain = get_conversational_chain()

    # Pass documents directly as expected by the chain
    response = chain(
        {"input_documents": docs, "question": user_question}, 
        return_only_outputs=True
    )
   
    # Display the response
    print(response)
    st.write("Reply: ", response['output_text'])


def main():
    #st.set_page_config(page_title="Chat with PDF")

    st.header("Chat with PDF using Gemini")

    user_question = st.text_input("Ask a question")

    if user_question:
        user_input(user_question)
    
    with st.sidebar:
        st.title("Menu :")
        # Allow multiple files
        pdf_docs = st.file_uploader("Upload your PDF Files and click submit", accept_multiple_files=True, type=["pdf"])

        if st.button("submit & Process"):
            with st.spinner("processing...."):
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)
                st.success("Done")


if __name__ == "__main__":
    main()