import streamlit as st
import base64
from groq import Groq

# Initialize Groq client
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# Function to encode uploaded image to base64
def encode_image(uploaded_file):
    try:
        if uploaded_file is not None:
            image_data = uploaded_file.read()
            encoded_image = base64.b64encode(image_data).decode("utf-8")
            return f"data:image/jpeg;base64,{encoded_image}"
        return None
    except Exception as e:
        st.error(f"Error processing image: {e}")
        return None

# Function to call Grok API
def get_grok_response(prompt, uploaded_file=None):
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt}
            ]
        }
    ]
    
    if uploaded_file:
        encoded_image = encode_image(uploaded_file)
        if encoded_image:
            messages[0]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {"url": encoded_image}
                }
            )
    
    try:
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling Groq API: {e}")
        return None

# Streamlit UI
st.set_page_config(page_title="Grok Chatbot", page_icon="🤖")
st.title("Grok Chatbot 🤖")
st.markdown("Ask me anything, with or without an image! Upload an image directly from your device.")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input form
with st.form(key="user_input_form"):
    uploaded_file = st.file_uploader("Upload Image (optional)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=False)
    prompt = st.text_area("Your Prompt", placeholder="Type your question or prompt here...")
    submit_button = st.form_submit_button(label="Send")

# Handle form submission
if submit_button and prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt, "uploaded_file": uploaded_file})

    # Get Grok response
    response = get_grok_response(prompt, uploaded_file)

    # Add assistant response to chat history
    if response:
        st.session_state.messages.append({"role": "assistant", "content": response})

# Display chat history in chatbot style
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user" and message.get("uploaded_file"):
            st.markdown(f"**You:** {message['content']}")
            st.image(message["uploaded_file"], caption="Uploaded Image", use_container_width=True)
        else:
            st.markdown(message["content"])

# Add some styling for chatbot vibe
st.markdown(
    """
    <style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stChatMessage[data-user="user"] {
        background-color: #DCF8C6;
    }
    .stChatMessage[data-user="assistant"] {
        background-color: #ECECEC;
    }
    </style>
    """,
    unsafe_allow_html=True
)