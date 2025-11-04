import streamlit as st
import pandas as pd
from datetime import date

# --- App Settings ---
st.set_page_config(page_title="Step & Calorie Challenge", page_icon="💪", layout="centered")
INVITE_CODE = "NOV2025"

# --- Initialize session storage ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "name" not in st.session_state:
    st.session_state.name = ""

# --- Data store (in-memory for now) ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=["Name", "Date", "Steps", "Calories", "Score"])

# --- Helper functions ---
def calculate_score(steps, calories):
    """50% from steps (out of 12,000) + 50% from calories (out of 400)"""
    step_score = min(steps / 12000, 1)
    cal_score = min(calories / 400, 1)
    return round((step_score * 0.5 + cal_score * 0.5) * 100, 2)

def highlight_top3(row, sorted_df):
    if row["Name"] == sorted_df.iloc[0]["Name"]:
        return ['background-color: gold'] * len(row)
    elif len(sorted_df) > 1 and row["Name"] == sorted_df.iloc[1]["Name"]:
        return ['background-color: silver'] * len(row)
    elif len(sorted_df) > 2 and row["Name"] == sorted_df.iloc[2]["Name"]:
        return ['background-color: #cd7f32'] * len(row)
    else:
        return [''] * len(row)

# --- Login Page ---
if not st.session_state.logged_in:
    st.title("💪 Step & Calorie Challenge")
    st.subheader("Login to get started")

    code = st.text_input("Enter Invite Code")
    name = st.text_input("Enter Your Name")

    if st.button("Login"):
        if code == INVITE_CODE and name.strip() != "":
            st.session_state.logged_in = True
            st.session_state.name = name.strip().title()
            st.success(f"Welcome, {st.session_state.name}! 🎉")
            st.experimental_rerun()
        else:
            st.error("Invalid code or name. Please try again.")
    st.stop()

# --- Main App ---
st.title("🏃‍♀️ Daily Tracker")

st.write(f"Welcome, **{st.session_state.name}**!")
today = date.today()

# Log entry form
st.subheader("Log Your Daily Progress")
steps = st.number_input("Steps Walked", min_value=0, max_value=50000, step=100)
calories = st.number_input("Calories Burned", min_value=0, max_value=2000, step=10)

if st.button("Submit Entry"):
    score = calculate_score(steps, calories)
    new_entry = pd.DataFrame({
        "Name": [st.session_state.name],
        "Date": [today],
        "Steps": [steps],
        "Calories": [calories],
        "Score": [score]
    })
    # Remove old entry for the same date + name
    st.session_state.data = st.session_state.data[~(
        (st.session_state.data["Name"] == st.session_state.name) &
        (st.session_state.data["Date"] == today)
    )]
    # Append new one
    st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
    st.success("Your entry has been saved!")

# --- Leaderboard ---
st.subheader("🏆 Leaderboard")
if len(st.session_state.data) > 0:
    leaderboard = st.session_state.data.groupby("Name", as_index=False)["Score"].mean().sort_values("Score", ascending=False)
    st.dataframe(leaderboard.style.apply(highlight_top3, axis=1, sorted_df=leaderboard))
else:
    st.info("No data yet. Log your first entry to appear on the leaderboard!")

# --- Visual progress ---
if len(st.session_state.data) > 0:
    latest_entry = st.session_state.data[st.session_state.data["Name"] == st.session_state.name].sort_values("Date").iloc[-1]
    st.subheader("📊 Today's Progress")
    st.progress(min(latest_entry["Steps"]/12000, 1.0))
    st.write(f"Steps: {latest_entry['Steps']}/12,000")
    st.progress(min(latest_entry["Calories"]/400, 1.0))
    st.write(f"Calories: {latest_entry['Calories']}/400")

st.caption("Invite Code: NOV2025 | Built with Streamlit 💡")
