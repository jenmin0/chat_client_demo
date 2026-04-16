import streamlit as st
from pydantic_agent import support_agent, Deps
from tools import get_account_info, get_transactions, calculate_summary, _execute_tool, ACCOUNTS

st.title("Bank Agent")

# Initialize session_state, ensuring that the state is preserved across page refreshes
if "agent" not in st.session_state:
    # Create pydantic agent, set prompt, register three banking tools
    st.session_state.agent = support_agent

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

if "history" not in st.session_state:
    st.session_state.history = []

# Handle user input and generate response
if prompt := st.chat_input("Ask about an account..."):
    # Show user message in chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    deps = Deps(accounts=ACCOUNTS)
    result = st.session_state.agent.run_sync(prompt,deps=deps,message_history=st.session_state.history)
    st.session_state.history += result.new_messages()
    response = result.output
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)