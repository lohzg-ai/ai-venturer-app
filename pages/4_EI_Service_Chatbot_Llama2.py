import streamlit as st
import uuid
import sys

import kendra_chat_bedrock_claudev2 as bedrock_claudev2
import kendra_chat_falcon_40b as falcon40b
import kendra_chat_llama_2 as llama2

USER_ICON = "images/user-icon.png"
EISER_ICON = "images/EI-SER-Logo.png"
AI_ICON = "images/EI-SER-Logo.png"
MAX_HISTORY_LENGTH = 5
PROVIDER_MAP = {
    "bedrock_claude": "Bedrock Claude",
    "bedrock_claudev2": "Bedrock Claude V2",
    'llama2' : 'Llama 2',
    'falcon40b': 'Falcon 40B'
}

st.set_page_config(
    page_title = "EI Service Chatbot",
    page_icon = "💻"
)

ECDA_Contact_Us_Page = "https://www.ecda.gov.sg/contact-us"

# Check user type
if 'user_type' not in st.session_state:
    st.session_state['user_type'] = ""


#function to read a properties file and create environment variables
def read_properties_file(filename):
    import os
    import re
    with open(filename, 'r') as f:
        for line in f:
            m = re.match(r'^\s*(\w+)\s*=\s*(.*)\s*$', line)
            if m:
                os.environ[m.group(1)] = m.group(2)


# Check if the user ID is already stored in the session state
if 'user_id' in st.session_state:
    user_id = st.session_state['user_id']

# If the user ID is not yet stored in the session state, generate a random UUID
else:
    user_id = str(uuid.uuid4())
    st.session_state['user_id'] = user_id


if 'llm_chain3' not in st.session_state:
    if (len(sys.argv) > 1):
        if (sys.argv[3] == 'bedrock_claudev2'):
            st.session_state['llm_app3'] = bedrock_claudev2
            st.session_state['llm_chain3'] = bedrock_claudev2.build_chain()
        elif (sys.argv[3] == 'llama2'):
            st.session_state['llm_app3'] = llama2
            st.session_state['llm_chain3'] = llama2.build_chain()
        elif (sys.argv[3] == 'falcon'):
            st.session_state['llm_app3'] = falcon40b
            st.session_state['llm_chain3'] = falcon40b.build_chain()
        else:
            raise Exception("Unsupported LLM: ", sys.argv[1])
    else:
        raise Exception("Usage: streamlit run app.py <bedrock_claude|bedrock_claudev2|llama2|falcon40b>")

if 'chat_history3' not in st.session_state:
    st.session_state['chat_history3'] = []
    
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

if "chats3" not in st.session_state:
    st.session_state.chats3 = [
        {
            'id': 0,
            'question': '',
            'answer': ''
        }
    ]

if "questions3" not in st.session_state:
    st.session_state.questions3 = []

if "answers3" not in st.session_state:
    st.session_state.answers3 = []

if "input3" not in st.session_state:
    st.session_state.input3 = ""

# CN - 21 Jan 2024
st.session_state['llm_app'] = st.session_state['llm_app3']
st.session_state['llm_chain'] = st.session_state['llm_chain3']
st.session_state['chat_history'] = st.session_state['chat_history3']
st.session_state.chats = st.session_state.chats3        
st.session_state.questions = st.session_state.questions3
st.session_state.answers = st.session_state.answers3
st.session_state.input = st.session_state.input3

chat_provider = sys.argv[3]

st.markdown("""
        <style>
               .block-container {
                    padding-top: 32px;
                    padding-bottom: 32px;
                    padding-left: 0;
                    padding-right: 0;
                }
                .element-container img {
                    background-color: #000000;
                }

                .main-header {
                    font-size: 25px;
                }
        </style>
        """, unsafe_allow_html=True)

# def write_logo():
#     col1, col2, col3 = st.columns([5, 1, 5])
#     with col2:
#         st.image(AI_ICON, use_column_width='always') 


def write_top_bar():
    col1, col2, col3 = st.columns([3,8,2])
    with col1:
        st.image(EISER_ICON,use_column_width=False,width=150)
    with col2:
        selected_provider = sys.argv[3]
        if selected_provider in PROVIDER_MAP:
            provider = PROVIDER_MAP[selected_provider]
        else:
            provider = selected_provider.capitalize()
        header = f"EI Service Chatbot"
        powered_by = f"Powered by Amazon Kendra and {provider} !"
        st.title(header)
        st.caption(powered_by)
    with col3:
        clear = st.button("Clear Chat")
    return clear

if st.session_state.user_type == "":
    st.write("")
else:
    clear = write_top_bar()

    if clear:
        st.session_state.questions = []
        st.session_state.answers = []
        st.session_state.input = ""
        st.session_state["chat_history"] = []
        st.session_state.questions3 = []
        st.session_state.answers3 = []
        st.session_state.input3 = ""
        st.session_state["chat_history3"] = []

    
def handle_input():
    input = st.session_state.input
    question_with_id = {
        'question': input,
        'id': len(st.session_state.questions)
    }
    st.session_state.questions.append(question_with_id)
    
    # Managing Chat History
    chat_history = st.session_state["chat_history"]
    if len(chat_history) == MAX_HISTORY_LENGTH:
        chat_history = chat_history[:-1]

    llm_chain = st.session_state['llm_chain']
    chain = st.session_state['llm_app']
    result = chain.run_chain(llm_chain, input, chat_history)
    answer = result['answer']
    chat_history.append((input, answer))
    
    document_list = []
    if 'source_documents' in result:
        for d in result['source_documents']:
            if not (d.metadata['source'] in document_list):
                document_list.append((d.metadata['source']))

    st.session_state.answers.append({
        'answer': result,
        'sources': document_list,
        'id': len(st.session_state.questions)
    })
    st.session_state.input = ""
    # CN - Added 21 Jan 2024
    st.session_state['llm_app3'] = st.session_state['llm_app']
    st.session_state['llm_chain3'] = st.session_state['llm_chain']
    st.session_state['chat_history3'] = st.session_state['chat_history']
    st.session_state.chats3 = st.session_state.chats        
    st.session_state.questions3 = st.session_state.questions
    st.session_state.answers3 = st.session_state.answers
    st.session_state.input3 = st.session_state.input    
    

def write_user_message(md):
    col1, col2 = st.columns([1,12])
    
    with col1:
        st.image(USER_ICON, use_column_width='always')
    with col2:
        st.warning(md['question'])


def render_result(result):
    answer, sources = st.tabs(['Answer', 'Sources'])
    with answer:
        render_answer(result['answer'])
    with sources:
        if 'source_documents' in result:
            render_sources(result['source_documents'])
        else:
            render_sources([])

def render_answer(answer):
    col1, col2 = st.columns([1,12])
    with col1:
        st.image(AI_ICON, use_column_width='always')
    with col2:
        st.info(answer['answer'])

def render_sources(sources):
    col1, col2 = st.columns([1,12])
    with col2:
        with st.expander("Sources"):
            for s in sources:
                st.write(s)

    
#Each answer will have context of the question asked in order to associate the provided feedback with the respective question
def write_chat_message(md, q):
    chat = st.container()
    with chat:
        render_answer(md['answer'])
        render_sources(md['sources'])
    

with st.container():
    for (q, a) in zip(st.session_state.questions, st.session_state.answers):
        write_user_message(q)
        write_chat_message(a, q)

st.markdown("")
if st.session_state.user_type == "":
    st.error("Please proceed to login...")
else:
    with st.sidebar:
         st.link_button("Contact Us", ECDA_Contact_Us_Page)
    input = st.text_input("You are talking to EI Service AI. Input your question below...", key="input", on_change=handle_input)
    st.markdown("---")
    with st.expander("Session State"):
        st.write(st.session_state)

