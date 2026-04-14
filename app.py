import streamlit as st
from client import OpenAIClient
from tools import get_account_info, get_transactions, calculate_summary, _execute_tool

st.title("Bank Agent")

# Initialize session_state, ensuring that the state is preserved across page refreshes
if "agent" not in st.session_state:
    # Create OpenAIClient, set prompt, register three banking tools
    st.session_state.agent = OpenAIClient(model="gpt-4o-mini")
    st.session_state.agent.set_system_prompt("You are a professional bank agent. You can use the following tools to help you answer user questions: 1. get_account_info(account_id): Get account information based on account_id. 2. get_transactions(account_id, start_date, end_date):Get the last n transactions for account_id and format them as strings e.g. :2026-04-10 | +€3000.00 | Salary 3. calculate_summary(account_id, n): Calculate the total in, total out and net for the last n transactions. tota;_in = sum of all amount > 0. total_out = sum of all amount < 0 (absolute value). net = total_in - total_out. Output format: Last 5 transactions | In: €3000.00 | Out: €850.00 | Net: +€2150.00")
    st.session_state.agent.register_tool(get_account_info,"Get account information by account_id.", {"type":"object",
                                            "properties":{
                                                "account_id": {
                                                    "type": "string",
                                                    "description": "The account id to get information for."
                                                }
                                            },
                                            "required": ["account_id"]})
    st.session_state.agent.register_tool(get_transactions,"Get the last n transactions for account_id.", {"type":"object",
                                        "properties": {
                                            "account_id": {
                                                "type": "string",
                                                "description": "The account id for which to get transactions."
                                            },
                                            "n": {
                                                "type": "integer",
                                                "description": "The number of transactions to retrieve."
                                            }
                                        },
                                    "required": ["account_id"]
                                    })
    st.session_state.agent.register_tool(calculate_summary,"Calculate the total in, total out and net for the last n transactions.", {"type":"object",
                                        "properties": {
                                            "account_id": {
                                                "type": "string",
                                                "description": "The account id for which to calculate summary."
                                            },
                                            "n": {
                                                "type": "integer",
                                                "description": "The number of transactions to include in the summary."
                                            }
                                        },
                                    "required": ["account_id"]
                                    })

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Handle user input and generate response
if prompt := st.chat_input("Ask about an account..."):
    # Show user message in chat
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    response = st.session_state.agent.chat_with_tools_and_history(prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.write(response)