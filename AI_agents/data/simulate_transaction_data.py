import random
from datetime import datetime, timedelta
import uuid
from faker import Faker
import sys
import json

# Initialize Faker for realistic fake data
fake = Faker()

def generate_random_payment():
    # Generate random date within the last 2 years
    random_days = random.randint(0, 1200)
    payment_date = (datetime.now() - timedelta(days=random_days)).strftime('%Y-%m-%d')

    # Generate random payment description
    payment_types = [
        "Salary Payment",
        "Online Shopping",
        "Utility Bill",
        "Restaurant Payment",
        "Grocery Store",
        "ATM Withdrawal",
        "Bank Transfer",
        "Subscription Payment",
        "Rent Payment",
        "Credit Card Payment"
    ]
    description = random.choice(payment_types)

    # Generate random account name (sender or recipient)
    account_name = fake.name()

    # Generate random account number
    account_number = str(random.randint(10000000, 99999999))

    # Generate random payment value (positive or negative)
    value = round(random.uniform(-5000, 5000), 2)

    # Generate random email
    email = fake.email()

    # Additional useful fields
    payment_id = str(uuid.uuid4())
    currency = random.choice(['USD', 'EUR', 'GBP', 'JPY', 'CAD'])
    status = random.choice(['Completed', 'Pending', 'Failed', 'Processing'])
    category = random.choice(['Income', 'Expense', 'Transfer', 'Investment'])

    # Create payment dictionary
    payment_data = {
        'payment_id': payment_id,
        'date': payment_date,
        'description': description,
        'account_name': account_name,
        'account_number': account_number,
        'value': value,
        'email': email,  # Added email field
        'currency': currency,
        'status': status,
        'category': category,
        'reference': fake.iban(),
        'bank_name': fake.company()
    }

    return payment_data

# Generate multiple payments
def generate_multiple_payments(count=100):
    return [generate_random_payment() for _ in range(count)]

# Example usage
if __name__ == "__main__":
    n = int(100)

    payments = generate_multiple_payments(n)
    file_name = f"simulated_data.json"

    with open(file_name, "w") as f:
        json.dump(payments, f, indent=4)

    print(f"✅ wrote {n} payments to {file_name}")
