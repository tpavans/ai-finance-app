import streamlit as st
import os
import math
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="AI Finance App",
    page_icon="💰",
    layout="centered"
)

# =========================
# CSV FILES
# =========================
DASHBOARD_FILE = "dashboard_data.csv"
EXPENSE_FILE = "monthly_expenses.csv"
GOLD_FILE = "gold_loans.csv"
HEALTH_FILE = "health_expenses.csv"
SIP_FILE = "sip_data.csv"
EMI_FILE = "emi_data.csv"

# =========================
# SAVE TO CSV
# =========================
def save_to_csv(data, filename):
    now = datetime.now()
    data["Date"] = now.strftime("%Y-%m-%d")
    data["Time"] = now.strftime("%H:%M:%S")
    df_new = pd.DataFrame([data])
    if os.path.exists(filename):
        df_old = pd.read_csv(filename)
        df = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df = df_new
    df.to_csv(filename, index=False)

# =========================
# LOAD API
# =========================
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# =========================
# INIT AI
# =========================
AI_AVAILABLE = True
try:
    if not GOOGLE_API_KEY:
        raise Exception("No API Key")
    llm = ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        temperature=0.6,
        timeout=30
    )
except:
    AI_AVAILABLE = False

# =========================
# PROMPT
# =========================
finance_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""
You are an Indian financial advisor.
Give:
1. Analysis
2. Budget
3. Investment
4. SIP
5. Emergency Fund
6. Risk
7. Action Plan
Use simple language.
"""),
    HumanMessagePromptTemplate.from_template(
        "Data:\n{user_input}"
    )
])

# =========================
# TITLE
# =========================
st.title("💰 AI Personal Finance Manager")
st.caption("All-in-One Money Manager 🇮🇳")

# =========================
# SIDEBAR
# =========================
menu = st.sidebar.selectbox(
    "📌 Menu",
    [
        "Dashboard",
        "SIP Calculator",
        "EMI Calculator",
        "Gold Loan",
        "Monthly Expenses",
        "Health Expenses",
        "Reports",
        "About"
    ]
)

# =========================
# DASHBOARD
# =========================
# =========================
# DASHBOARD (FIXED)
# =========================
# =========================
# DASHBOARD (CURRENT ONLY)
# =========================
if menu == "Dashboard":

    st.subheader("📊 Financial Dashboard")

    # User inputs
    income = st.number_input("Monthly Income ₹", 0)
    expense = st.number_input("Monthly Expense ₹", 0)
    savings = st.number_input("Current Savings ₹", 0)
    goal = st.number_input("Goal Amount ₹", 0)
    months = st.number_input("Goal Duration (Months)", 1)

    # Current EMI & Gold Loan inputs (for dashboard only)
    emi_pending = st.number_input("Pending EMI ₹ (current loan)", 0)
    gold_pending = st.number_input("Pending Gold Loan ₹ (current loan)", 0)

    if st.button("🚀 Analyze"):

        if income <= 0:
            st.warning("Enter valid income")
            st.stop()

        monthly_save = income - expense
        total_liabilities = emi_pending + gold_pending

        # Display current input summary only
        st.markdown("### 💡 Summary (Current Input Only)")
        st.info(f"Monthly Income: ₹{income:,.0f}")
        st.info(f"Monthly Expense: ₹{expense:,.0f}")
        st.info(f"Current Savings: ₹{savings:,.0f}")
        st.info(f"Monthly Saving: ₹{monthly_save:,.0f}")
        st.info(f"Goal Amount: ₹{goal:,.0f} in {months} months")
        st.info(f"Pending EMI: ₹{emi_pending:,.0f}")
        st.info(f"Pending Gold Loan: ₹{gold_pending:,.0f}")
        st.warning(f"Total Liabilities: ₹{total_liabilities:,.0f}")

        # Colorful bar chart
        fig, ax = plt.subplots()
        categories = ["Income", "Expense", "Savings", "Monthly Save", "Total Liabilities"]
        values = [income, expense, savings, monthly_save, total_liabilities]
        colors = ["#3498DB", "#E74C3C", "#2ECC71", "#F1C40F", "#9B59B6"]
        ax.bar(categories, values, color=colors)
        ax.set_ylabel("₹ Amount")
        ax.set_title("📊 Financial Overview (Current Data)")
        st.pyplot(fig)

        # AI Report (current input only)
        data = f"""
Income: {income}
Expense: {expense}
Savings: {savings}
Monthly Save: {monthly_save}
Goal: {goal}
Months: {months}
Pending EMI: {emi_pending}
Pending Gold Loan: {gold_pending}
Total Liabilities: {total_liabilities}
"""
        if AI_AVAILABLE:
            try:
                with st.spinner("🤖 AI Analyzing..."):
                    msg = finance_prompt.format_messages(user_input=data)
                    res = llm.invoke(msg).content
            except:
                res = "AI Busy. Try later."
        else:
            res = f"""
Offline Report
Monthly Saving: ₹{monthly_save}
Emergency Fund: ₹{expense*6}
Start SIP: ₹{monthly_save*0.4:.0f}
Pending EMI: ₹{emi_pending}
Pending Gold Loan: ₹{gold_pending}
Total Liabilities: ₹{total_liabilities}
"""

        st.markdown("### 📋 AI Report")
        st.write(res)

        # Optionally store current input to CSV for reports
        save_to_csv({
            "Income": income,
            "Expense": expense,
            "Savings": savings,
            "Monthly Save": monthly_save,
            "Goal": goal,
            "Pending EMI": emi_pending,
            "Pending Gold Loan": gold_pending,
            "Total Liabilities": total_liabilities,
            "Report": res
        }, DASHBOARD_FILE)
# =========================
# SIP CALCULATOR
# =========================
elif menu == "SIP Calculator":
    st.subheader("📈 SIP Calculator")
    amt = st.number_input("Monthly SIP ₹", 0.0)
    rate = st.number_input("Return % per year", 0.0)
    yrs = st.number_input("Years", 1)

    if st.button("Calculate SIP"):
        n = yrs * 12
        r = rate / 100 / 12 if rate != 0 else 0
        final_value = amt * ((1+r)**n - 1)/r*(1+r) if r != 0 else amt * n
        total_invested = amt * n
        yearly_investment = amt * 12
        profit = final_value - total_invested

        st.success("✅ SIP Calculation Complete")
        st.info(f"Monthly Investment: ₹{amt:,.0f}")
        st.info(f"Yearly Investment: ₹{yearly_investment:,.0f}")
        st.info(f"Total Invested: ₹{total_invested:,.0f}")
        st.info(f"Profit Earned: ₹{profit:,.0f}")
        st.warning(f"Final Maturity Value: ₹{final_value:,.0f}")

        save_to_csv({
            "Monthly SIP": amt,
            "Yearly Investment": yearly_investment,
            "Total Invested": total_invested,
            "Profit": profit,
            "Final Value": final_value
        }, SIP_FILE)

# =========================
# EMI CALCULATOR
# =========================
elif menu == "EMI Calculator":
    st.subheader("🏦 EMI Calculator")
    loan = st.number_input("Loan Amount ₹", 0.0)
    rate = st.number_input("Interest % per year", 0.0)
    yrs = st.number_input("Loan Tenure (Years)", 1)
    paid_months = st.number_input("Months Already Paid", 0, step=1)

    if st.button("Calculate EMI"):
        n = yrs * 12
        r = rate / 12 / 100 if rate != 0 else 0
        monthly_emi = loan*r*(1+r)**n/((1+r)**n-1) if r != 0 else loan/n
        yearly_emi = monthly_emi * 12
        total_payment = monthly_emi * n
        total_interest = total_payment - loan
        paid_amount = paid_months * monthly_emi
        remaining_amount = max(total_payment - paid_amount, 0)
        status = "Loan Completed ✅" if remaining_amount == 0 else f"Loan Pending ⏳ Remaining: ₹{remaining_amount:,.0f}"

        st.success("✅ EMI Calculation Complete")
        st.info(f"Monthly EMI: ₹{monthly_emi:,.0f}")
        st.info(f"Yearly EMI: ₹{yearly_emi:,.0f}")
        st.info(f"Total Payment: ₹{total_payment:,.0f}")
        st.info(f"Total Interest: ₹{total_interest:,.0f}")
        st.warning(status)

        save_to_csv({
            "Loan": loan,
            "Monthly EMI": monthly_emi,
            "Yearly EMI": yearly_emi,
            "Total Payment": total_payment,
            "Total Interest": total_interest,
            "Months Paid": paid_months,
            "Remaining Amount": remaining_amount,
            "Status": status
        }, EMI_FILE)

# =========================
# GOLD LOAN
# =========================
elif menu == "Gold Loan":
    st.subheader("🥇 Gold Loan")
    weight = st.number_input("Gold Weight (grams)", 0.0)
    rate = st.number_input("Interest % per year", 0.0)
    months = st.number_input("Loan Tenure (Months)", 1)
    paid_months = st.number_input("Months Already Paid", 0, step=1)

    gold_price = 5000
    loan_amount = weight * gold_price
    interest = loan_amount * rate / 100 * months / 12
    total_payable = loan_amount + interest
    monthly_payment = total_payable / months
    paid_amount = paid_months * monthly_payment
    remaining_amount = max(total_payable - paid_amount, 0)
    status = "Loan Completed ✅" if remaining_amount == 0 else f"Loan Pending ⏳ Remaining: ₹{remaining_amount:,.0f}"

    if st.button("Calculate Gold Loan"):
        st.success(f"Loan Amount: ₹{loan_amount:,.0f}")
        st.info(f"Interest: ₹{interest:,.0f}")
        st.info(f"Monthly Payment: ₹{monthly_payment:,.0f}")
        st.warning(f"Total Payable: ₹{total_payable:,.0f}")
        st.warning(status)

        save_to_csv({
            "Weight": weight,
            "Loan Amount": loan_amount,
            "Interest": interest,
            "Monthly Payment": monthly_payment,
            "Total Payable": total_payable,
            "Months Paid": paid_months,
            "Remaining Amount": remaining_amount,
            "Status": status
        }, GOLD_FILE)

# =========================
# MONTHLY EXPENSES
# =========================
elif menu == "Monthly Expenses":
    st.subheader("🧾 Monthly Expenses")
    groceries = st.number_input("Groceries ₹", 0)
    milk = st.number_input("Milk ₹", 0)
    electricity = st.number_input("Electricity ₹", 0)
    emi = st.number_input("EMI ₹", 0)
    mobile = st.number_input("Mobile ₹", 0)
    others = st.number_input("Others ₹", 0)
    total = groceries + milk + electricity + emi + mobile + others

    if st.button("Save Expenses"):
        save_to_csv({
            "Groceries": groceries,
            "Milk": milk,
            "Electricity": electricity,
            "EMI": emi,
            "Mobile": mobile,
            "Others": others,
            "Total": total
        }, EXPENSE_FILE)
        st.success(f"Saved: ₹{total:,.0f}")

# =========================
# HEALTH EXPENSES
# =========================
elif menu == "Health Expenses":
    st.subheader("🏥 Health Expenses")
    doctor = st.number_input("Doctor ₹", 0)
    medicine = st.number_input("Medicine ₹", 0)
    test = st.number_input("Tests ₹", 0)
    hospital = st.number_input("Hospital ₹", 0)
    total = doctor + medicine + test + hospital

    if st.button("Save Health Data"):
        save_to_csv({
            "Doctor": doctor,
            "Medicine": medicine,
            "Test": test,
            "Hospital": hospital,
            "Total": total
        }, HEALTH_FILE)
        st.success(f"Saved: ₹{total:,.0f}")

# =========================
# REPORTS
# =========================
elif menu == "Reports":
    st.subheader("📊 Reports")
    for file, name in [(DASHBOARD_FILE,"Dashboard"),(EXPENSE_FILE,"Monthly Expenses"),
                       (GOLD_FILE,"Gold Loans"),(HEALTH_FILE,"Health Expenses"),
                       (SIP_FILE,"SIP Investments"),(EMI_FILE,"EMI Loans")]:
        if os.path.exists(file):
            st.write(f"### {name}")
            st.dataframe(pd.read_csv(file))

# =========================
# ABOUT
# =========================
else:
    st.subheader("ℹ️ About")
    st.markdown("""
## 💼 AI Personal Finance Services provided
Smart money manager for Indian users 🇮🇳

### Features
✅ AI Advisor  
✅ SIP / EMI  
✅ Gold Loan  
✅ Expense Tracker  
✅ Health Tracker  
✅ Reports  

### Developer
Made by **Pavansai** ❤️
""")

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown("""
<center>
💻 Built with Python & Streamlit 🚀<br>
AI Personal Finance Manager<br>
 Developed By Pavansai
</center>
""", unsafe_allow_html=True)