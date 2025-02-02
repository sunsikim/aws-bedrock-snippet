import os
import boto3
import streamlit as st
from dotenv import load_dotenv
from bedrock_snippet.old_services.prompt_management import PromptManagementService


@st.cache_resource
def start_session() -> boto3.Session:
    load_dotenv()
    return boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


session = start_session()
prompt_name = st.text_input("prompt name (REQUIRED)")
system_prompt = st.text_area("system prompt (REQUIRED)", height=300)
user_prompt = st.text_area("user prompt (REQUIRED)", height=100)
with st.expander("Prompt Configuration", expanded=False):
    description = st.text_input("prompt description")
    temperature = st.slider(
        "temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.1
    )
    max_tokens = st.number_input(
        "max tokens", min_value=100, max_value=2000, value=2000
    )
    top_k = st.number_input("top K", min_value=1, max_value=1000, value=50)
col1, col2 = st.columns(2)
with col1:
    st.button("generate")
with col2:
    st.button("create snapshot", type="primary")
