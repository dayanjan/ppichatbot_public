import streamlit as st
from openai import OpenAI

# Instantiate the OpenAI client
client = OpenAI(api_key="YOUR_API_KEY_HERE") 

# Setting page title and header
hide_streamlit_style = """<style> #MainMenu {visibility: hidden;} footer {visibility: hidden;} </style>"""
st.set_page_config(page_title="PPI-Chat Experimental AI", page_icon=":robot:")
header_html = """
    <img src='https://pharmacy.vcu.edu/media/pharmacy/images/homepage/bm_SchoolOfPharmacy_RF_rd_hz_4c_rev.png' 
    alt='VCU School of Pharmacy Logo' style='width:100%; height:auto; margin-bottom:100px;'>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
st.markdown(header_html, unsafe_allow_html=True)

# Read system message from the text file
system_message_path = "SystemMessage/systemmessage.txt"
try:
    with open(system_message_path, "r") as file:
        system_message = file.read().strip()
except FileNotFoundError:
    system_message = "System message not found. Please check the file path."

# Initialise session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []
    if system_message:
        st.session_state.messages.append({"role": "system", "content": system_message})

# Sidebar for model selection and cost tracking
st.sidebar.title("Model selection and cost tracking")
model_name = st.sidebar.radio("Choose a model:", ("GPT-4", "GPT-3.5"))
model = "gpt-3.5-turbo" if model_name == "GPT-3.5" else "gpt-4"
counter_placeholder = st.sidebar.empty()
clear_button = st.sidebar.button("Clear Conversation")

# Clear conversation and re-add system message if it exists
if clear_button:
    st.session_state.messages = []
    if system_message:
        st.session_state.messages.append({"role": "system", "content": system_message})

# Use a form for user input to prevent continuous repetition
with st.form(key="user_input_form", clear_on_submit=True):
    user_input = st.text_input("You:", key="input")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input:
    # Update chat history with user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Generate response from OpenAI API using the instantiated client
    completion = client.chat.completions.create(
        model=model,
        messages=st.session_state.messages,
        temperature=0.7  # Adjust temperature as needed
    )
    response = completion.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": response})

# Place the function and download button after the conversation is updated
# Functionality to save conversation history, excluding system messages
def save_conversation(messages):
    filtered_messages = [msg for msg in messages if msg["role"] != "system"]  # Exclude system messages
    conversation_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in filtered_messages])
    return conversation_text

# Ensure conversation_text is updated right before rendering the download button
conversation_text = save_conversation(st.session_state.messages)
st.sidebar.download_button(
    label="Save Conversation",
    data=conversation_text,
    file_name="conversation_history.txt",
    mime="text/plain"
)

# Display conversation
for message in reversed(st.session_state.messages):
    if message["role"] in ["user", "assistant"]:  # Only display user and assistant messages
        # Calculate dynamic height based on the number of lines (approximation)
        lines = message["content"].count('\n') + 1
        height = max(50, lines * 20)  # Increase height as needed

        # Define custom styles for user and assistant messages
        if message["role"] == "user":
            background_color = "#F28500"  # Soft orange for user messages
            text_color = "white"  # White text for better contrast
        else:
            background_color = "#2B8EAD"  # Dark blue for assistant messages
            text_color = "white"  # White text for better contrast

        # Use Markdown with unsafe_allow_html to apply custom styles
        message_html = f"""
        <div style="background-color: {background_color}; color: {text_color}; padding: 10px; border-radius: 10px; margin: 5px 0; height: auto; max-height: 300px; overflow-y: auto;">
            {message["content"]}
        </div>
        """
        st.markdown(message_html, unsafe_allow_html=True)
