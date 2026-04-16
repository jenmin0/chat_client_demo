from pydantic_ai import Agent, RunContext
from dataclasses import dataclass
from dotenv import load_dotenv
import os

from tools import ACCOUNTS, get_account_info, get_transactions, calculate_summary


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@dataclass
class Deps:  
  accounts: dict

support_agent = Agent(  
    'openai:gpt-4o-mini',  
    deps_type=Deps,
    instructions=(  
        'You are a support agent in our bank, give the customer support.'
    ),
)

@support_agent.tool  
def tool_get_account_info(
    ctx: RunContext[Deps], account_id: str) -> str:
    """Get account information by account_id.
        If account_id does not exist, return 'Account not found'
        If it exists, return a string, e.g.:
        Account A001 | Owner: Max Müller | Balance: €24350.00 | Status: active
        """  
    return get_account_info(account_id)

@support_agent.tool  
def tool_get_transactions(
    ctx: RunContext[Deps], account_id: str, n: int) -> str:
    """Get the last n transactions for account_id and format them as strings e.g. :
    2026-04-10 | +€3000.00 | Salary
    """
    return get_transactions(account_id, n)

@support_agent.tool  
def tool_calculate_summary(
    ctx: RunContext[Deps], account_id: str, n: int) -> str:
    """Calculate the total in, total out and net for the last n transactions.
    tota;_in = sum of all amount > 0
    total_out = sum of all amount < 0 (absolute value)
    net = total_in - total_out
    Output format:
    Last 5 transactions | In: €3000.00 | Out: €850.00 | Net: +€2150.00
    """
    return calculate_summary(account_id, n)

def main():
  deps = Deps(accounts=ACCOUNTS)
  result = support_agent.run_sync('Give me the account info for A001, last 5 transactions, and the summary.', deps=deps)
  print(result.output)

# main()