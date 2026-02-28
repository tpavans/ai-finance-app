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

if menu == "Dashboard":

    st.subheader("📊 Financial Dashboard")

    income = st.number_input("Monthly Income ₹", 0)
    expense = st.number_input("Monthly Expense ₹", 0)
    savings = st.number_input("Current Savings ₹", 0)
    goal = st.number_input("Goal Amount ₹", 0)
    months = st.number_input("Goal Duration (Months)", 1)


    if st.button("🚀 Analyze"):

        if income <= 0:
            st.warning("Enter valid income")
            st.stop()


        monthly_save = income - expense


        data = f"""
Income: {income}
Expense: {expense}
Savings: {savings}
Monthly Save: {monthly_save}
Goal: {goal}
Months: {months}
"""


        # AI / Offline
        if AI_AVAILABLE:

            try:
                with st.spinner("🤖 AI Analyzing..."):

                    msg = finance_prompt.format_messages(
                        user_input=data
                    )

                    res = llm.invoke(msg).content

            except:
                res = "AI Busy. Try later."

        else:

            res = f"""
Offline Report

Monthly Saving: ₹{monthly_save}
Emergency Fund: ₹{expense*6}
Start SIP: ₹{monthly_save*0.4:.0f}
"""


        # SAVE
        save_to_csv({

            "Income": income,
            "Expense": expense,
            "Savings": savings,
            "Monthly Save": monthly_save,
            "Goal": goal,
            "Report": res

        }, DASHBOARD_FILE)


        st.success("✅ Report Generated")

        st.metric("Monthly Saving", f"₹{monthly_save}")


        # CHART
        fig, ax = plt.subplots()

        ax.bar(
            ["Income", "Expense", "Saving"],
            [income, expense, monthly_save]
        )

        st.pyplot(fig)


        st.markdown("### 📋 AI Report")
        st.write(res)



# =========================
# SIP
# =========================

elif menu == "SIP Calculator":

    st.subheader("📈 SIP Calculator")

    amt = st.number_input("Monthly SIP ₹", 0.0)
    rate = st.number_input("Return %", 0.0)
    yrs = st.number_input("Years", 1)


    if st.button("Calculate SIP"):

        n = yrs * 12

        if rate == 0:
            final = amt * n
        else:
            r = rate / 100 / 12

            final = amt * ((1+r)**n - 1)/r*(1+r)


        invested = amt * n
        profit = final - invested


        st.success(f"Final Value: ₹{final:,.0f}")
        st.info(f"Profit: ₹{profit:,.0f}")



# =========================
# EMI
# =========================

elif menu == "EMI Calculator":

    st.subheader("🏦 EMI Calculator")

    loan = st.number_input("Loan Amount ₹", 0.0)
    rate = st.number_input("Interest %", 0.0)
    yrs = st.number_input("Years", 1)


    if st.button("Calculate EMI"):

        n = yrs * 12


        if rate == 0:
            emi = loan / n

        else:
            r = rate / 12 / 100

            emi = loan*r*(1+r)**n/((1+r)**n-1)


        total = emi*n
        interest = total - loan


        st.success(f"Monthly EMI: ₹{emi:,.0f}")
        st.info(f"Total Interest: ₹{interest:,.0f}")



# =========================
# GOLD LOAN
# =========================

elif menu == "Gold Loan":

    st.subheader("🥇 Gold Loan")

    weight = st.number_input("Gold Weight (grams)", 0.0)
    rate = st.number_input("Interest %", 0.0)
    months = st.number_input("Months", 1)


    amount = weight * 5000


    if st.button("Calculate Gold Loan"):

        interest = amount * rate/100 * months/12
        total = amount + interest


        st.success(f"Loan: ₹{amount:,.0f}")
        st.info(f"Interest: ₹{interest:,.0f}")
        st.warning(f"Total: ₹{total:,.0f}")


        save_to_csv({

            "Weight": weight,
            "Loan": amount,
            "Interest": interest,
            "Total": total

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


    if os.path.exists(DASHBOARD_FILE):
        st.write("### Dashboard")
        st.dataframe(pd.read_csv(DASHBOARD_FILE))


    if os.path.exists(EXPENSE_FILE):
        st.write("### Monthly Expenses")
        st.dataframe(pd.read_csv(EXPENSE_FILE))


    if os.path.exists(GOLD_FILE):
        st.write("### Gold Loans")
        st.dataframe(pd.read_csv(GOLD_FILE))


    if os.path.exists(HEALTH_FILE):
        st.write("### Health Expenses")
        st.dataframe(pd.read_csv(HEALTH_FILE))



# =========================
# ABOUT
# =========================

else:

    st.subheader("ℹ️ About")

    st.markdown("""

## 💼 AI Finance App

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
By Pavansai
</center>
""", unsafe_allow_html=True)