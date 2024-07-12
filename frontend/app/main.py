import streamlit as st
import asyncio
import aiohttp
from datetime import datetime
from helpers.format_response import format_response
from helpers.persist_session_state import save_session_state, load_session_state
from helpers.make_request import make_request
from utils.logs import setup_logger
from consts import URL, PERSIST_DIR, SESSION_ID
import pandas as pd
from io import BytesIO

logger = setup_logger(__name__)

persist_file_path = PERSIST_DIR + f'{SESSION_ID}_session_state.json'
load_session_state(st.session_state, file_path=persist_file_path)


async def retrieve_bot_response(user_input, session_id):
    async with aiohttp.ClientSession() as session:
        payload = {"query": user_input, "user_id": 'try',
                                        "slack_id": session_id, "llm_type": 'gpt'}
        print(payload)
        data = await make_request(session, 'get', f'{URL}/agent/ask_question',
                                  json=payload)
        if "agent_response" in data.keys():
            agent_response = data["agent_response"]
        else:
            agent_response = data

        response = agent_response['response']
        tokens_used = agent_response['tokens_used']
        total_cost = agent_response['total_cost']
        response_type = agent_response['response_type']
        explanation = agent_response['explanation']
        last_code_executed = agent_response['last_code_executed']
        conversation_id = agent_response['conversation_id']
        logger.info('This is the response..')
        logger.info(response)
        logger.debug('Session context before response..')

        logger.info(f'Response type is {response_type}')

        if response_type == "plot" or response_type == "dataframe":
            file_info = data.get('file')
            if file_info:
                filename, file_data = file_info
                file_data = bytes(file_data)  # Convert bytearray to bytes
                with open(filename, "wb") as f:
                    f.write(file_data)
                st.write('File uploaded:', filename)
                st.download_button('Download file', data=file_data, file_name=filename)
                if filename.endswith(('png', 'jpg', 'jpeg')):
                    st.image(file_data, caption=filename)
                elif filename.endswith('csv'):
                    df = pd.read_csv(BytesIO(file_data))
                    st.dataframe(df)
        else:
            st.markdown(response)

        # Process the response
        counter = 0
        with st.empty():
            stream_data = ""
            try:
                counter += 1
                if "error" in response:
                    stream_data = response["error"]

                if counter == 1:
                    stream_data = response
                st.markdown(stream_data)
            except asyncio.TimeoutError:
                st.warning("Connection timed out. Closing the connection.")

        return stream_data


st.title("Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Accept user input
if prompt := st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Collect conversation history for the payload
    conversation_history = "\n".join([msg["content"] for msg in st.session_state.messages if msg["role"] == "user"])

    # Logging to check conversation history is saved
    logger.info(f"Current conversation history: {conversation_history}")

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        st.markdown('**Time:** ' + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        full_response = asyncio.new_event_loop().run_until_complete(
            retrieve_bot_response(prompt, SESSION_ID)
        )

    # Add assistant response to chat history
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response, "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    logger.debug(f"Assistant response added to chat history: {full_response}")

    save_session_state(st.session_state, file_path=persist_file_path)
