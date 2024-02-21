import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationTokenBufferMemory
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import SKLearnVectorStore
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from .utils.utils import load_env
from PIL import Image

load_env()

@st.cache_resource
def openai_model(key):
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ["OPENAI_API_KEY"])
    return embeddings

@st.cache_resource(show_spinner="Loading vectorstore! Please wait.")
def vectordb(_embeddings):
    loader = CSVLoader(file_path='./apps/disease_explainer_chain/app/msd.csv',csv_args={'delimiter': ';','quotechar': '"','fieldnames': ['name','document', 'source']},source_column="source")
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size= 100, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    vectordb = SKLearnVectorStore.from_documents(documents=docs,embedding=_embeddings)
    return vectordb

def load_prompt():
    system_template = """You are a virtual assistant specifically designed for aiding in differential diagnosis. Your primary task is to provide potential explanations for a given set of symptoms, organizing these explanations from the most probable to the least probable causes. Additionally, you should detail related symptoms for each possible cause. When presented with symptoms, you should actively ask for more information if it could help in narrowing down or excluding certain diagnoses.\
Your responses should be structured to present a clear and logical flow of reasoning. Remember to process and incorporate any clinical results or additional information as they are provided, adjusting your differential diagnosis accordingly. You are supporting medical professionals in their diagnostic process, so precision and clarity in your responses are paramount.\
It's imperative that you don't ever answer questions that are not about disease. In that case say you don't have any information about it.\
Use the context sto answer to the questions. Limit your knowledge to the provided context, nothing else.\
Keep the answers short.\
Use the same scientific terms and expressions as the one in the context when providing the answer.\
Example 1:\
Q: Who is Albert Einstein?\
A: I apologize, I don't have any information about that.\
Example 2:\
Q: What is the French Revolution?\
A: I'm sorry, I can only answer questions about medical deseases.\
Example 3:\
Q: What happened on 9/11?\
A: I'm sorry, I don't have any information about that.\
Example 4:\
Q: What is diabetes?\
A: Diabetes mellitus is impaired insulin secretion and variable degrees of peripheral insulin resistance leading to hyperglycemia.\
Example 5:\
Q: What are the symptoms of diabetes?\
A: Early symptoms are related to hyperglycemia and include polydipsia, polyphagia, polyuria, and blurred vision.\
---
Context:
{context}
---
Chat history: {chat_history}"""

    system_prompt = PromptTemplate(template=system_template,input_variables=['context', 'chat_history'])
    partial_prompt = system_prompt.partial()
    system_template_prompt = SystemMessagePromptTemplate(prompt=partial_prompt) 
    messages = [system_template_prompt,HumanMessagePromptTemplate.from_template("{question}")]
    return ChatPromptTemplate.from_messages(messages)   

@st.cache_resource
def load_chain(_prompt_template,_vectorstore):
    retriever = _vectorstore.as_retriever(search_type='mmr', search_kwargs={'k': 2})
    llm = ChatOpenAI(temperature=0, openai_api_key=os.environ["OPENAI_API_KEY"])
    conversational_memory = ConversationTokenBufferMemory(llm=llm,memory_key='chat_history',
                                            return_messages=True,
                                            output_key="answer",
                                            max_token_limit=1800)
    chain = ConversationalRetrievalChain.from_llm(llm=llm,
                                            memory=conversational_memory,
                                            combine_docs_chain_kwargs={'prompt':_prompt_template},
                                            verbose=True,
                                            retriever=retriever,
                                            max_tokens_limit=1800,
                                            return_source_documents=True)
    return chain


def generate_response(query,chain):
    response = chain({"question": query})
    return response

embeddings = openai_model(st.secrets["OPENAI_API_KEY"])
vectorstore = vectordb(embeddings)
prompt = load_prompt()
desease_chain = load_chain(prompt,vectorstore)


def main():
    from . import app_description, app_name
    image = Image.open('./apps/desease_explainer_chain/app/stethoscope.png')
    st.image(image)
    st.title(app_name)
    st.divider()
    st.write(app_description)
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        if message['role'] == 'assistant':
            avatar_img = 'https://cdn2.iconfinder.com/data/icons/medical-health-18/32/expaded_health-line_icon_09-512.png'
        else:
            avatar_img = 'data:image/png;base64,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'
        with st.chat_message(message["role"], avatar=avatar_img):
            st.markdown(message["content"])

    if user_input:= st.chat_input("Example: What is the common flu?"):
        response = generate_response(user_input,desease_chain)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user", avatar='data:image/png;base64,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'):
            st.markdown(user_input)
        with st.chat_message('assistant', avatar='https://media.istockphoto.com/id/1364448514/vector/stethoscope-icon-vector-stethoscope-icon-for-medical-design.jpg?s=612x612&w=0&k=20&c=DXnAQgqevXLxd2M650fk5TUligIklWRgsxsJvzm3Hqs='):
            answer = response['ansert'] + ' Source: ' + response['source_documents'][0].metadata['source']
            st.write(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

if __name__ == '__main__':
    main()

