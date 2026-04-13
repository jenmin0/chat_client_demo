import random
from datetime import datetime, timedelta


# Mock data
ACCOUNTS = {
    "A001": {"owner": "Max Müller",   "balance": 24350.00, "status": "active"},
    "A002": {"owner": "Anna Schmidt", "balance": 8120.50,  "status": "active"},
    "A003": {"owner": "Tom Weber",    "balance": 310.00,   "status": "frozen"},
}

TOOL_REGISTRY = {
    "get_weather": get_weather,
    "calculate": calculate,
    "get_account_info": get_account_info,
    "get_transactions": get_transactions,
    "calculate_summary": calculate_summary
}

def _execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute the tool and return the result."""

    for t_name, t_function in TOOL_REGISTRY.items():
        if t_name == tool_name:
            return t_function(**arguments)
        else:
            return f"Tool {tool_name} not found."

    

def get_weather(city: str)  -> str:
    """Example tool function to get weather information."""
    return f"{city} today is sunny with a high of 25°C."

def calculate(expression: str) -> str:
    return str(eval(expression))

def _generate_transactions(account_id: str, n: int = 10)    -> list:
    """Generate mock transactions, with consistent results for each account_id"""
    random.seed(account_id)
    transactions = []
    for i in range(n):
        date = datetime.today() - timedelta(days=i*3)
        amount = round(random.uniform(-2000, 3000), 2)
        transactions.append({
            "date": date.strftime("%Y-%m-%d"),
            "amount": amount,
            "type": "credit" if amount > 0 else "debit",
            "description": random.choice(["Salary", "Rent", "Transfer", "Purchase", "Refund"])
        })
    return transactions


def get_account_info(account_id: str) -> str:
    """Get account information by account_id.
    If account_id does not exist, return 'Account not found'
    If it exists, return a string, e.g.:
    Account A001 | Owner: Max Müller | Balance: €24350.00 | Status: active
    """
    if account_id not in ACCOUNTS:
        return "Account not found"
    account = ACCOUNTS[account_id]
    return f"Account: {account_id} | Owner: {account["owner"]} | Balance: {account["balance"]} | Status: {account["status"]}"
    

def get_transactions(account_id: str, n: int = 5) -> str:
    """Get the last n transactions for account_id and format them as strings e.g. :
    2026-04-10 | +€3000.00 | Salary
    """
    transactions = _generate_transactions(account_id, n)
    formatted_transactions = []
    for transaction in transactions:
        transaction_string = f"{transaction["date"]} | {'+' if transaction["amount"] > 0 else '-'}€{abs(transaction["amount"]):.2f} | {transaction["description"]}\n"
        formatted_transactions.append(transaction_string)

    return "".join(formatted_transactions)

def calculate_summary(account_id: str, n: int = 5) -> str:
    """Calculate the total in, total out and net for the last n transactions.
    tota;_in = sum of all amount > 0
    total_out = sum of all amount < 0 (absolute value)
    net = total_in - total_out
    Output format:
    Last 5 transactions | In: €3000.00 | Out: €850.00 | Net: +€2150.00
    """
    transactions = _generate_transactions(account_id, n)

    total_in = sum(transaction['amount'] if transaction['amount'] > 0 else 0 for transaction in transactions)
    total_out = sum(-transaction['amount'] if transaction['amount'] < 0 else 0 for transaction in transactions)
    net = total_in - total_out

    return f"Last {n} transactions | In: €{total_in:.2f} | Out: €{total_out:.2f} | Net: {'+' if net >= 0 else '-'}€{net:.2f}"