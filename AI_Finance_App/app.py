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

st.title("💰 AI Personal Finance Analyzing Services")
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
                with st.spinner("🤖 AI Analyzing..."):

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
#SIP
# =========================
# SIP Calculator
# =========================

elif menu == "SIP Calculator":

    st.subheader("📈 SIP Calculator")

    amt = st.number_input("Monthly SIP Amount ₹", min_value=0.0, step=500.0, format="%.2f")
    rate = st.number_input("Expected Return (% per year)", min_value=0.0, step=0.5, format="%.2f")
    yrs = st.number_input("Investment Period (Years)", min_value=1, step=1)

    if st.button("Calculate SIP"):

        n = int(yrs * 12)   # Total months

        if amt == 0:
            st.warning("⚠️ Please enter SIP amount")
            st.stop()

        # Monthly rate
        r = rate / 100 / 12

        # If return = 0
        if rate == 0:
            final_value = amt * n
        else:
            final_value = amt * ((1 + r) ** n - 1) / r * (1 + r)

        total_invested = amt * n
        yearly_investment = amt * 12
        profit = final_value - total_invested


        # Display Results
        st.success("✅ SIP Calculation Complete")

        st.markdown("### 📊 SIP Investment Details")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"📅 Monthly Investment\n\n₹{amt:,.2f}")
            st.info(f"📆 Yearly Investment\n\n₹{yearly_investment:,.2f}")

        with col2:
            st.info(f"💰 Total Invested\n\n₹{total_invested:,.2f}")
            st.info(f"📈 Profit Earned\n\n₹{profit:,.2f}")

        st.markdown("### 🏆 Final Maturity Value")
        st.success(f"₹{final_value:,.2f}")

# =========================
# EMI
# =========================
# EMI Calculator
# =========================

elif menu == "EMI Calculator":

    st.subheader("🏦 EMI Calculator")

    loan = st.number_input("Loan Amount ₹", min_value=0.0, step=1000.0, format="%.2f")
    rate = st.number_input("Interest Rate (% per year)", min_value=0.0, step=0.1, format="%.2f")
    yrs = st.number_input("Loan Tenure (Years)", min_value=1, step=1)

    if st.button("Calculate EMI"):

        n = int(yrs * 12)   # Total months

        if loan == 0:
            st.warning("⚠️ Please enter loan amount")
            st.stop()

        # If interest = 0
        if rate == 0:
            monthly_emi = loan / n
        else:
            r = rate / 12 / 100   # Monthly interest

            monthly_emi = loan * r * (1 + r) ** n / ((1 + r) ** n - 1)

        yearly_emi = monthly_emi * 12
        total_payment = monthly_emi * n
        total_interest = total_payment - loan


        # Display Results
        st.success("✅ EMI Calculation Complete")

        st.markdown("### 📊 EMI Details")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"📅 Monthly EMI\n\n₹{monthly_emi:,.2f}")
            st.info(f"📆 Yearly EMI\n\n₹{yearly_emi:,.2f}")

        with col2:
            st.info(f"💰 Total Payment\n\n₹{total_payment:,.2f}")
            st.info(f"📈 Total Interest\n\n₹{total_interest:,.2f}")
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

# =========================
# ABOUT
# =========================

else:

    st.subheader("ℹ️ About This App")

    st.markdown("""
## 💼 AI Personal Finance Manager

Welcome to **AI Finance App** — your smart assistant for managing money wisely 💰📊

### 🚀 Key Features
✅ Budget & Expense Planner  
✅ AI Financial Advisor  
✅ SIP & EMI Calculators  
✅ Interactive Charts  
✅ PDF Report Generator  
✅ Mobile-Friendly Interface  

### 🎯 Purpose
This app helps Indian users 🇮🇳:
- Track income & expenses  
- Plan savings  
- Grow investments  
- Manage loans  
- Improve financial discipline  

### 🛠️ Technology Used
🔹 Python  
🔹 Streamlit  
🔹 AI APIs  
🔹 Pandas & Matplotlib  

### 👨‍💻 Developer
Made with ❤️ by **Pavansai**  
B.Tech AIML Student | AI Enthusiast 🚀

---

📢 *"Smart Money = Strong Future"*
""")

# =========================
## =========================
# FOOTER
# =========================

st.markdown("---")

st.markdown("""
<div style="text-align: center; padding: 10px;">

💻 Built with <b>Python</b> & <b>Streamlit</b> 🚀<br>
📊 AI Personal Finance Manager<br>
👨‍💻 Developed by <b>Pavansai</b><br>
🇮🇳 Made for Indian Users

</div>
""", unsafe_allow_html=True)