import os
import sys
from dotenv import load_dotenv

load_dotenv()

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from rag import ask

qs = [
    ("Q1", "Which supplier had the highest spend in Q1, and what was its on-time delivery percentage?"),
    ("Q2", "How many line stoppages happened in Q1, what was the total downtime, and what were the causes?"),
    ("Q3", "What is the approval authority for a purchase order worth ₹1.4 crore?"),
    ("Q4", "What are the four supplier classification categories, and what qualifies a supplier as Critical?"),
    ("Q5", "Kaveri Metals recorded 88.1% on-time delivery and 1,150 defects per million in Q1. Which policy clauses does this trigger, and what exactly must the buyer do?"),
    ("Q6", "The microcontroller supplier is single-source. What does the sourcing policy require in this situation, and what is the company already doing about it?"),
    ("Q7", "Microcontrollers are imported with a 46-day lead time. Using the policy formula, what is the required safety stock in days?"),
    ("Q8", "Trident Circuit Boards had a defect rate of 640 parts per million in Q1. What is the policy consequence under Clause 6.3?"),
    ("Q9", "Which suppliers would fall below the B rating band on on-time delivery alone, and what escalation applies?"),
    ("Q10", "What is the annual salary of the Head of Procurement?")
]

print("=========================================================================")
print("EXACT GENERATED ANSWERS FOR ALL 10 ASSIGNMENT QUESTIONS")
print("=========================================================================")

for code, q in qs:
    res = ask(q)
    print(f"\n### {code}: {q}")
    print(f"**Answer**:\n{res['answer']}\n")
    print(f"**Sources**: {res['sources']}")
    print("-" * 75)
