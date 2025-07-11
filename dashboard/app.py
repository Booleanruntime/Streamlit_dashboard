import streamlit as st
import requests
import pandas as pd

# Config
API_BASE_URL = "https://ai-costops-backend.herokuapp.com"

st.set_page_config(page_title="AI CostOps Dashboard", layout="wide")

st.title("💸 AI API CostOps – PoC Dashboard")

# Fetch stats
def fetch_stats():
    resp = requests.get(f"{API_BASE_URL}/stats")
    return resp.json()

# Fetch logs
def fetch_logs():
    resp = requests.get(f"{API_BASE_URL}/logs")
    return resp.json()["logs"]

def simulate_switch_to_gpt35(ratio):
    payload = {"switch_to_gpt35_ratio": ratio}
    resp = requests.post(f"{API_BASE_URL}/simulate", json=payload)
    return resp.json()

def simulate_caching(cache_ratio):
    payload = {"cache_ratio": cache_ratio}
    resp = requests.post(f"{API_BASE_URL}/simulate_caching", json=payload)
    return resp.json()


# Display stats
with st.spinner("Fetching stats..."):
    stats = fetch_stats()
    total_cost = stats.get("total_cost_usd", 0)
    total_tokens = stats.get("total_tokens", 0)
    spend_by_model = stats.get("spend_by_model", [])

st.metric("Total API Spend (USD)", f"${total_cost:.4f}")
st.metric("Total Tokens Used", f"{total_tokens:,}")

# Spend by model
if spend_by_model:
    st.subheader("💡 Spend by Model")
    model_df = pd.DataFrame(spend_by_model)
    st.bar_chart(model_df.set_index("model"))

# Recent API Calls
st.subheader("📜 Recent API Calls (Last 100)")
with st.spinner("Fetching logs..."):
    logs = fetch_logs()

if logs:
    logs_df = pd.DataFrame(logs)
    logs_df["timestamp"] = pd.to_datetime(logs_df["timestamp"], unit="s")
    st.dataframe(logs_df.sort_values("timestamp", ascending=False))
else:
    st.info("No API logs found yet. Make some calls!")

def fetch_recommendations():
    resp = requests.get(f"{API_BASE_URL}/recommendations")
    return resp.json()["recommendations"]

# Add below logs
st.subheader("💡 Savings Recommendations")
with st.spinner("Analyzing your usage..."):
    recs = fetch_recommendations()

for rec in recs:
    st.warning(rec)
    
st.subheader("🔄 Simulate Savings")
st.write("📉 See how much you could save by moving some GPT-4 traffic to GPT-3.5.")

# Slider to choose % of GPT-4 traffic to switch
switch_ratio = st.slider(
    "Switch this % of GPT-4 traffic to GPT-3.5", min_value=10, max_value=100, step=10
) / 100.0

if st.button("Simulate Savings"):
    with st.spinner("Calculating..."):
        sim_result = simulate_switch_to_gpt35(switch_ratio)

    st.success(f"💰 Original Spend: ${sim_result['original_cost']:.4f}")
    st.success(f"💡 Simulated Spend: ${sim_result['simulated_cost']:.4f}")
    st.metric("Potential Savings", f"${sim_result['potential_savings']:.4f}")

st.subheader("🧊 Simulate Caching Savings")
st.write("📦 What if repeated prompts were cached instead of re-sent?")

cache_ratio = st.slider(
    "Cache this % of repeated prompts", min_value=10, max_value=100, step=10
) / 100.0

if st.button("Simulate Caching Savings"):
    with st.spinner("Calculating caching impact..."):
        cache_result = simulate_caching(cache_ratio)

    st.success(f"💰 Original Spend: ${cache_result['original_cost']:.4f}")
    st.success(f"💡 Simulated Spend: ${cache_result['simulated_cost']:.4f}")
    st.metric("Potential Savings from Caching", f"${cache_result['potential_savings']:.4f}")
