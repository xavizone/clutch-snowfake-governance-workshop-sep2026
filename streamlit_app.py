# Clutch Horizon Context Demo — Streamlit presentation app
import streamlit as st
import os

conn = st.connection("snowflake", ttl=os.getenv("SNOWFLAKE_CONNECTION_TTL"))

st.session_state["conn"] = conn
st.session_state["SCHEMA"] = "CUST_DEMO_DB.CLUTCH_HORIZON"

page = st.navigation({
    "": [
        st.Page("app_pages/overview.py", title="Overview", icon=":material/home:"),
        st.Page("app_pages/setup.py", title="Setup", icon=":material/build:"),
    ],
    "Horizon Capabilities": [
        st.Page("app_pages/classification.py", title="1. Classification", icon=":material/fingerprint:"),
        st.Page("app_pages/masking.py", title="2. Masking Policies", icon=":material/visibility_off:"),
        st.Page("app_pages/lineage.py", title="3. Data Lineage", icon=":material/account_tree:"),
        st.Page("app_pages/trust_center.py", title="4. Trust Center", icon=":material/security:"),
        st.Page("app_pages/data_quality.py", title="5. Data Quality", icon=":material/check_circle:"),
        st.Page("app_pages/ai_context.py", title="6. AI Context Layer", icon=":material/psychology:"),
        st.Page("app_pages/semantic_agent.py", title="7. Semantic + Agent", icon=":material/hub:"),
        st.Page("app_pages/rbac_enforcement.py", title="8. RBAC Enforcement", icon=":material/shield:"),
    ],
    "Lab Guide": [
        st.Page("app_pages/coco_prompts.py", title="9. CoCo Prompts", icon=":material/chat:"),
    ],
}, position="sidebar")

st.sidebar.divider()
st.sidebar.caption("Snowflake Horizon Context — Hands-On Lab")
st.sidebar.caption("CUST_DEMO_DB.CLUTCH_HORIZON")

page.run()
