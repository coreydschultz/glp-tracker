#!/usr/bin/env python3
"""
GLP-1 Journey Tracker - Retatrutide
Streamlit app for tracking weight, dosage, and side effects
"""

import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import plotly.express as px
import plotly.graph_objects as go

# Config
st.set_page_config(page_title="GLP-1 Journey", page_icon="💪", layout="wide")

DATA_FILE = "glp1_data.csv"

# Load or initialize data
@st.cache_data
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df['date'] = pd.to_datetime(df['date']).dt.date
        return df
    return pd.DataFrame(columns=[
        'date', 'weight', 'dose', 'nausea', 'fatigue', 'gi', 'sleep', 'notes'
    ])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)
    st.cache_data.clear()

# Initialize
df = load_data()

# Sidebar - Add new entry
st.sidebar.header("💉 Log Today's Data")
st.sidebar.markdown("---")

with st.sidebar.form("entry_form"):
    entry_date = st.date_input("Date", date.today())
    entry_weight = st.number_input("Weight (lbs)", min_value=0.0, max_value=500.0, step=0.1)
    entry_dose = st.number_input("Dose (mg)", min_value=0.0, max_value=20.0, step=0.5)
    
    st.markdown("### Side Effects (0-10)")
    entry_nausea = st.slider("Nausea 🤢", 0, 10, 0)
    entry_fatigue = st.slider("Fatigue 😴", 0, 10, 0)
    entry_gi = st.slider("GI Issues 💩", 0, 10, 0)
    entry_sleep = st.slider("Sleep Issues 😵", 0, 10, 0)
    
    entry_notes = st.text_area("Notes", placeholder="Any other observations...")
    
    submitted = st.form_submit_button("Save Entry")
    
    if submitted:
        new_row = pd.DataFrame([{
            'date': entry_date,
            'weight': entry_weight,
            'dose': entry_dose,
            'nausea': entry_nausea,
            'fatigue': entry_fatigue,
            'gi': entry_gi,
            'sleep': entry_sleep,
            'notes': entry_notes
        }])
        df = pd.concat([df, new_row], ignore_index=True).sort_values('date')
        save_data(df)
        st.success("Saved! 🎉")
        st.rerun()

# Main content
st.title("💪 GLP-1 Journey: Retatrutide")

# Show data stats
if not df.empty:
    latest = df.iloc[-1]
    start = df.iloc[0]
    weight_loss = start['weight'] - latest['weight'] if start['weight'] and latest['weight'] else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Current Weight", f"{latest['weight']:.1f} lbs")
    col2.metric("Total Loss", f"{weight_loss:.1f} lbs" if weight_loss > 0 else f"+{abs(weight_loss):.1f} lbs")
    col3.metric("Current Dose", f"{latest['dose']:.1f} mg")
    col4.metric("Days Tracking", (pd.to_datetime(latest['date']) - pd.to_datetime(start['date'])).days)
    
    st.markdown("---")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📊 Weight Chart", "💉 Dosage Log", "🤢 Side Effects", "📋 Data Table"])

with tab1:
    st.subheader("Weight Over Time")
    if len(df) > 1:
        # Weight chart
        fig = px.scatter(df, x='date', y='weight', 
                        title="Weight Loss Journey",
                        labels={'date': 'Date', 'weight': 'Weight (lbs)'})
        fig.add_hline(y=start['weight'], line_dash="dash", line_color="red", 
                     annotation_text="Start")
        st.plotly_chart(fig, use_container_width=True)
        
        # Weekly change
        if len(df) >= 7:
            weekly = df.tail(7)
            weekly_change = weekly.iloc[0]['weight'] - weekly.iloc[-1]['weight']
            st.metric("This Week", f"{weekly_change:+.1f} lbs")
    else:
        st.info("Log at least 2 weigh-ins to see the chart! 📈")

with tab2:
    st.subheader("Dosage Timeline")
    if not df.empty:
        fig = px.bar(df, x='date', y='dose', 
                    title="Dose Over Time",
                    labels={'date': 'Date', 'dose': 'Dose (mg)'},
                    color='dose',
                    color_continuous_scale='Greens')
        st.plotly_chart(fig, use_container_width=True)
        
        # Dosage schedule reference
        st.markdown("### Standard Titration Schedule")
        schedule = pd.DataFrame({
            'Week': [1, 2, 3, 4, 5, 6, 7, 8],
            'Dose (mg)': [2, 4, 6, 8, 10, 12, 12, 12]
        })
        st.table(schedule)
    else:
        st.info("Log your doses above! 💉")

with tab3:
    st.subheader("Side Effects Tracker")
    if not df.empty:
        # Side effects over time
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['date'], y=df['nausea'], name="Nausea 🤢", line=dict(color='red')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['fatigue'], name="Fatigue 😴", line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['gi'], name="GI Issues 💩", line=dict(color='brown')))
        fig.add_trace(go.Scatter(x=df['date'], y=df['sleep'], name="Sleep 😵", line=dict(color='purple')))
        
        fig.update_layout(title="Side Effects Over Time", 
                         yaxis_title="Severity (0-10)",
                         xaxis_title="Date")
        st.plotly_chart(fig, use_container_width=True)
        
        # Average side effects
        st.markdown("### Average Side Effects")
        avg_cols = st.columns(4)
        avg_cols[0].metric("Nausea", f"{df['nausea'].mean():.1f}/10")
        avg_cols[1].metric("Fatigue", f"{df['fatigue'].mean():.1f}/10")
        avg_cols[2].metric("GI", f"{df['gi'].mean():.1f}/10")
        avg_cols[3].metric("Sleep", f"{df['sleep'].mean():.1f}/10")
    else:
        st.info("Log side effects in the sidebar! 📝")

with tab4:
    st.subheader("All Data")
    if not df.empty:
        # Build list of entries for selectbox
        df['display'] = df.apply(lambda r: f"{r['date']} | {r['weight']} lbs | {r['dose']}mg", axis=1)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🗑️ Delete Entry")
            entry_to_delete = st.selectbox("Select entry to delete", options=[""] + df['display'].tolist(), key="delete_select")
            if st.button("Delete", key="delete_btn") and entry_to_delete:
                idx = df[df['display'] == entry_to_delete].index[0]
                df = df.drop(idx).reset_index(drop=True)
                df = df.drop('display', axis=1)
                save_data(df)
                st.success("Deleted!")
                st.rerun()
        
        with col2:
            st.markdown("✏️ Edit Entry")
            entry_to_edit = st.selectbox("Select entry to edit", options=[""] + df['display'].tolist(), key="edit_select")
            if entry_to_edit:
                idx = df[df['display'] == entry_to_edit].index[0]
                row = df.iloc[idx]
                
                new_weight = st.number_input("Weight", value=float(row['weight']), key="edit_weight")
                new_dose = st.number_input("Dose", value=float(row['dose']), key="edit_dose")
                new_nausea = st.slider("Nausea", 0, 10, int(row['nausea']), key="edit_nausea")
                new_fatigue = st.slider("Fatigue", 0, 10, int(row['fatigue']), key="edit_fatigue")
                new_gi = st.slider("GI Issues", 0, 10, int(row['gi']), key="edit_gi")
                new_sleep = st.slider("Sleep", 0, 10, int(row['sleep']), key="edit_sleep")
                new_notes = st.text_area("Notes", value=str(row['notes']) if pd.notna(row['notes']) else "", key="edit_notes")
                
                if st.button("Save Changes", key="save_btn"):
                    df.at[idx, 'weight'] = new_weight
                    df.at[idx, 'dose'] = new_dose
                    df.at[idx, 'nausea'] = new_nausea
                    df.at[idx, 'fatigue'] = new_fatigue
                    df.at[idx, 'gi'] = new_gi
                    df.at[idx, 'sleep'] = new_sleep
                    df.at[idx, 'notes'] = new_notes
                    df = df.drop('display', axis=1)
                    save_data(df)
                    st.success("Saved!")
                    st.rerun()
        
        df = df.drop('display', axis=1)
        
        st.markdown("### 📋 All Entries")
        st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)
        
        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button("Download CSV 📥", csv, "glp1_data.csv", "text/csv")
    else:
        st.info("No data yet. Start logging! 📋")

# Footer
st.markdown("---")
st.caption(f"GLP-1 Journey Tracker | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
