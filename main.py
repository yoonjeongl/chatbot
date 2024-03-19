# Standard library imports
import time
import openai

# Third-Party Imports
import streamlit as st

# Importing other files for setup and functionalities
from setup_st import set_design, sidebar, get_user_config, clear_button, download_button, initialize_session_state
from helper_functions import generate_response, generate_response_index
from index_functions import load_data

# Initialize session state variables if they don't exist
initialize_session_state()

# Setup Streamlit UI/UX elements
set_design()
sidebar()
get_user_config()
clear_button()
download_button()

# Setting up environment variables for OpenAI API key
if 'api_key' in st.session_state and st.session_state['api_key']:
    openai.api_key = st.session_state['api_key']

# Setting up indexing functionality
try:
    index = load_data()
    chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True)
except Exception as e:
    st.sidebar.error(f"An error occurred while loading indexed data: {e}")

# Warning to show that index is not currently being used if checkbox is unchecked
if not st.session_state['use_index']:
    st.sidebar.warning("Index is not currently being used. Toggle box above if you'd like to enable it.")

# Displaying the existing chat messages from the user and the chatbot
for message in st.session_state.messages:  # For every message in the chat history
    with st.chat_message(message["role"]):  # Create a chat message box
        st.markdown(message["content"])  # Display the content of the message

# Accept user input and generate response
if prompt := st.chat_input("How would you like to reply?"):
    
    # Add user's message to the chat history
    if prompt != "":
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt}) # Add user's message to chat history

    # Increment total message count
    st.session_state['message_count'] += 1

    # Call either generate_response or generate_response_index based on st.session_state['use_index']
    if st.session_state['use_index']:
        response_generated = generate_response_index(
            "You are an expert who is great at assisting users with whatever query they have",
            st.session_state.messages,
            st.session_state['model_name'],
            st.session_state['temperature'],
            chat_engine
        )
    else:
        response_generated = generate_response(
            "You are an expert who is great at assisting users with whatever query they have",
            st.session_state.messages,
            st.session_state['model_name'],
            st.session_state['temperature']
        )
    
    # Create spinner to indicate to the user that the assistant is generating a response
    with st.spinner('CoPilot is thinking...'):
        
        # Create a chat message box for displaying the assistant's response
        with st.chat_message("assistant"):
            
            # Initialize an empty string to construct the full response incrementally
            full_response = ""
            
            # Create an empty placeholder to stream the assistant's response
            message_placeholder = st.empty()
            
            # Loop through the response generator
            for response in response_generated:
                
                # If the full_response is not empty, display it and save to message history
                if full_response:
                    message_placeholder.markdown(full_response)
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                # Reset full_response and create a new empty placeholder
                full_response = ""
                message_placeholder = st.empty()
                
                # Break the content into chunks of 10 words each
                chunks = response["content"].split(' ')
                full_response = ""
                
                # Loop through the chunks to simulate a 'typing' effect
                for i in range(0, len(chunks), 10):
                    
                    # Join the next 10 words to form a chunk
                    chunk = ' '.join(chunks[i:i+10])
                    
                    # Add the chunk to the full response string
                    full_response += chunk + " "  # Add a space at the end of each chunk
                    
                    # Display the currently generated text followed by a 'typing' cursor
                    message_placeholder.markdown(full_response + "▌")
                    
                    # Wait for a small amount of time to simulate the typing effect
                    time.sleep(0.2)
                    
            # Remove the 'typing' cursor and display the final full response
            message_placeholder.markdown(full_response)
            
            # Add the assistant's final full response to the session state message history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
    # Code to update the progress bar; assuming a message cap of 10 messages, but can be changed to be dynamic depending on your implementation.
    current_progress = st.progress(st.session_state['message_count'] / 10)
