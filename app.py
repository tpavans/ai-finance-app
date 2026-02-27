import streamlit as st
import os
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from fpdf import FPDF

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
# SESSION HISTORY
# =========================

if "history" not in st.session_state:
    st.session_state.history = []


# =========================
# TITLE
# =========================

st.title("💰 AI Personal Finance Super App")
st.caption("All-in-One Money Manager 🇮🇳")


# =========================
# SIDEBAR
# =========================

menu = st.sidebar.radio(
    "📌 Menu",
    ["Dashboard", "SIP Calculator", "EMI Calculator", "History", "About"]
)


# =========================
# DASHBOARD
# =========================

if menu == "Dashboard":

    st.subheader("📊 Financial Dashboard")

    col1, col2 = st.columns(2)

    with col1:
        income = st.number_input("Monthly Income ₹", 0, step=500)

    with col2:
        expense = st.number_input("Monthly Expense ₹", 0, step=500)

    savings = st.number_input("Current Savings ₹", 0, step=1000)

    goal = st.number_input("Goal Amount ₹", 0, step=5000)

    months = st.number_input("Goal Duration (Months)", 1, step=1)


    if st.button("🚀 Analyze"):

        if income <= 0:
            st.warning("Enter valid income")
            st.stop()


        monthly_save = income - expense

        six = monthly_save * 6
        year = monthly_save * 12


        # Feasibility
        if monthly_save <= 0:
            feasible = "No"
            need = "Not Possible"
        else:
            need = math.ceil(
                max(0, goal - savings) / monthly_save
            )
            feasible = "Yes" if need <= months else "No"


        data = f"""
Income: {income}
Expense: {expense}
Savings: {savings}
Monthly Save: {monthly_save}
Goal: {goal}
Months: {months}
Needed: {need}
Feasible: {feasible}
"""


        # AI / Offline
        if AI_AVAILABLE:

            try:
                with st.spinner("🤖 AI Thinking..."):

                    msg = finance_prompt.format_messages(
                        user_input=data
                    )

                    res = llm.invoke(msg).content

            except:
                res = "AI busy. Try later."

        else:

            res = f"""
Offline Report:

Monthly Saving: ₹{monthly_save}
6 Month: ₹{six}
1 Year: ₹{year}

Emergency Fund: ₹{expense*6}

Try to save 20-30%.
Start SIP ₹{monthly_save*0.4:.0f}
"""


        # Save history
        st.session_state.history.append({
            "income": income,
            "expense": expense,
            "save": monthly_save,
            "goal": goal,
            "report": res
        })


        # DISPLAY
        st.success("Report Ready")

        st.metric("Monthly Saving", f"₹{monthly_save}")
        st.metric("1 Year Potential", f"₹{year}")


        # CHART
        fig, ax = plt.subplots()

        ax.bar(
            ["Income", "Expense", "Saving"],
            [income, expense, monthly_save]
        )

        st.pyplot(fig)


        st.markdown("### 📋 AI Report")
        st.write(res)


        # PDF
        if st.button("📥 Download PDF"):

            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)

            for line in res.split("\n"):
                pdf.multi_cell(0, 8, line)

            pdf.output("report.pdf")

            with open("report.pdf", "rb") as f:
                st.download_button(
                    "Download",
                    f,
                    file_name="finance_report.pdf"
                )


# =========================
# SIP
# =========================

elif menu == "SIP Calculator":

    st.subheader("📈 SIP Calculator")

    amt = st.number_input("Monthly SIP ₹", 500, step=500)
    rate = st.number_input("Return %", 1.0, step=0.5)
    yrs = st.number_input("Years", 1)

    if st.button("Calculate SIP"):

        r = rate / 100 / 12
        n = yrs * 12

        fv = amt * ((1+r)**n - 1) / r * (1+r)

        st.success(f"Final Value: ₹{fv:,.0f}")


# =========================
# EMI
# =========================

elif menu == "EMI Calculator":

    st.subheader("🏦 EMI Calculator")

    loan = st.number_input("Loan Amount ₹", 0)
    rate = st.number_input("Interest %", 1.0)
    yrs = st.number_input("Years", 1)

    if st.button("Calculate EMI"):

        r = rate / 12 / 100
        n = yrs * 12

        emi = loan*r*(1+r)**n/((1+r)**n-1)

        st.success(f"Monthly EMI: ₹{emi:,.0f}")


# =========================
# HISTORY
# =========================

elif menu == "History":

    st.subheader("📜 Reports History")

    if len(st.session_state.history) == 0:
        st.info("No history yet")

    else:
        df = pd.DataFrame(st.session_state.history)

        st.dataframe(df)


# =========================
# ABOUT
# =========================

else:

    st.subheader("ℹ️ About")

    st.write("""
This is an AI-powered finance app.

Features:
✔ Budget Planner
✔ AI Advisor
✔ SIP / EMI
✔ Charts
✔ PDF Reports
✔ Mobile Friendly

Built by You 💙
""")


# =========================
# FOOTER
# =========================

st.markdown("---")
st.caption("Powered by Gemini + Streamlit 🚀")