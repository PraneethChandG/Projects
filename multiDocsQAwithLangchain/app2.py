import streamlit as st
from PyPDF2 import PdfReader  # still here in case you plan to handle PDFs later
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai

from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
st.set_page_config(page_title="Chat with Python Files")

# ------------------------- Text Processing Functions -------------------------

def get_python_text(py_docs):
    """Reads and concatenates content from uploaded Python files"""
    text = ""
    for file in py_docs:
        content = file.read().decode("utf-8")
        text += content + "\n"
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return text_splitter.split_text(text)

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vector_store = FAISS.from_texts(text_chunks, embeddings)
    vector_store.save_local("faiss_index")

# ------------------------- Gemini QA Chain Setup -------------------------

def get_conversational_chain():
    prompt_template = """
You are a Python code review assistant. 
Evaluate the code based on efficiency, readability, and adherence to best practices and
generate the whole code with those changes.



Context:
{context}

Question:
{question}
"""
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.3)
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)
    return chain

# ------------------------- User Question Handler -------------------------

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    try:
        # Load FAISS index
        new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        chain = get_conversational_chain()
        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)
        st.write("Reply:", response['output_text'])
    except Exception as e:
        st.error(f"An error occurred while processing your question: {e}")

# ------------------------- Streamlit App UI -------------------------

def main():
    st.header("💬 Chat with Your Python Code (Gemini-powered)")

    user_question = st.text_input("Ask a question", placeholder="e.g., How can I improve my loop efficiency?")

    if user_question:
        user_input(user_question)

    with st.sidebar:
        st.title("📂 File Upload")
        py_files = st.file_uploader("Upload your Python files", accept_multiple_files=True, type=["py"])

        if st.button("Submit & Process"):
            if py_files:
                try:
                    with st.spinner("Processing files..."):
                        raw_text = get_python_text(py_files)
                        text_chunks = get_text_chunks(raw_text)
                        
                        if not os.path.exists("faiss_index/index.faiss"):
                            get_vector_store(text_chunks)
                        
                        st.success("Files processed and indexed successfully!")
                except Exception as e:
                    st.error(f"Failed to process files: {e}")
            else:
                st.warning("Please upload at least one Python file.")

if __name__ == "__main__":
    main()
