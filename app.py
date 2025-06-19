import pandas as pd
import streamlit as st
from datetime import datetime, timedelta

# --- Setup ---
st.set_page_config(page_title="Fleet Maintenance Dashboard", layout="wide")
st.title("✈️ Fleet Maintenance Scheduler")

# --- Load Data ---
df = pd.read_csv("data/fleet_status.csv", parse_dates=["last_check"])

# --- Calculate Next Due Date & Status ---
today = pd.Timestamp.today()
df["next_due"] = df["last_check"] + df["days_until_due"].apply(lambda x: timedelta(days=x))

def status_color(date):
    if date < today:
        return "🔴 Overdue"
    elif date < today + timedelta(days=7):
        return "🟠 Due Soon"
    else:
        return "🟢 OK"

df["status"] = df["next_due"].apply(status_color)

# --- Summary Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Aircraft", len(df))
col2.metric("Overdue", (df["status"] == "🔴 Overdue").sum())
col3.metric("Due in 7 Days", (df["status"] == "🟠 Due Soon").sum())

# --- Optional Sidebar Filter ---
st.sidebar.header("Filter Options")
if st.sidebar.checkbox("Filter by Check Type"):
    selected = st.sidebar.selectbox("Select Check Type", sorted(df["check_type"].unique()))
    df = df[df["check_type"] == selected]

# --- Prepare Table View ---
styled_df = df[["tail_number", "aircraft_type", "check_type", "last_check", "next_due", "status"]].sort_values("next_due")

def highlight_status(row):
    color = ""
    if row["status"] == "🔴 Overdue":
        color = "background-color: #ffcccc"
    elif row["status"] == "🟠 Due Soon":
        color = "background-color: #fff2cc"
    elif row["status"] == "🟢 OK":
        color = "background-color: #d4edda"
    return [color]*len(row)

# --- Display Styled Table ---
st.dataframe(
    styled_df.style.apply(highlight_status, axis=1),
    use_container_width=True
)

# --- Export Filtered Table ---
csv = styled_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Table as CSV",
    data=csv,
    file_name="fleet_maintenance_export.csv",
    mime="text/csv",
)
