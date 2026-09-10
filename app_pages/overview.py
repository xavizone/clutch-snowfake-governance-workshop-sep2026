# Overview page
# Co-authored with CoCo
import streamlit as st

st.title("Snowflake Horizon Context — Hands-On Lab")

st.markdown("""
### Why Horizon Matters

Modern data teams handle **customer PII, financial data, and operational records** under 
privacy regulations like **PIPEDA** and **GDPR**. With multiple BI tools querying Snowflake 
directly and AI workloads growing fast, governance at the Snowflake layer is the only approach 
that works consistently across every consumer of the data.

---

### What is Snowflake Horizon Context?

**Horizon Context** is Snowflake's unified governance and catalog framework. It provides the 
metadata, policies, and intelligence that make data **discoverable, understandable, and trustworthy** 
— whether that data lives inside Snowflake, in Iceberg tables, or across external systems.

The framework is built on **three foundational pillars:**
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("#### :material/link: Connect")
    st.markdown("""
    Unify your entire data estate
    - Apache Iceberg tables
    - Iceberg REST Catalog API
    - Catalog-linked databases
    - Internal Marketplace
    """)

with col2:
    st.markdown("#### :material/lightbulb: Context")
    st.markdown("""
    Enrich data with business meaning
    - Semantic Views
    - End-to-end lineage
    - Auto-generated descriptions
    - Object tagging
    """)

with col3:
    st.markdown("#### :material/verified_user: Trust")
    st.markdown("""
    Govern and protect automatically
    - Data classification
    - Masking & row access
    - AI Guardrails
    - Trust Center
    """)

st.markdown("""
---

### An Evolving Platform

Snowflake continuously adds new capabilities under the Horizon umbrella. Recent additions include:

| Capability | Status | What It Does |
|-----------|--------|-------------|
| **External Lineage (OpenLineage)** | GA Sep 2026 | dbt, Airflow lineage flows into Snowflake natively |
| **One-Click Remediation** | GA Aug 2026 | Trust Center generates and executes fix SQL |
| **Snowflake-Provided Tags** | PuPr Aug 2026 | Out-of-the-box tags: cost center, sensitivity, environment |
| **Data Quality Dashboard** | PuPr Jul 2026 | Account-wide data quality health view |
| **AI Guardrails** | GA | Prompt injection and jailbreak protection for AI agents |
| **Cortex Sense** | Coming soon | Proactive anomaly detection and insight discovery |
| **Intent-Driven Governance** | PuPr Aug 2026 | Natural language governance workflows via CoCo |

This lab covers the core capabilities available today. As Snowflake expands Horizon, 
the same governance foundation applies to every new feature.
""")

st.divider()

st.markdown("""
### Demo Data Model

This demo uses **CUST_DEMO_DB.CLUTCH_HORIZON** — a realistic Canadian eCommerce dataset 
modeled on a vehicle marketplace:

| Layer | Objects | Description |
|-------|---------|-------------|
| **RAW** | `RAW_CUSTOMERS`, `RAW_VEHICLES`, `RAW_TRANSACTIONS`, `RAW_WARRANTY_CLAIMS` | Source data with PII |
| **STG** | `STG_CUSTOMERS`, `STG_VEHICLES` | Staging views (cleaning) |
| **DIM/FCT** | `DIM_CUSTOMERS`, `FCT_SALES` | Dimension + fact tables (CTAS) |
| **RPT** | `RPT_CUSTOMER_SUMMARY`, `RPT_VEHICLE_RELIABILITY`, `RPT_SALES_BY_REGION` | Reporting views |

This creates a **3-layer lineage chain**: RAW → STG → DIM/FCT → RPT
""")

conn = st.session_state["conn"]
df = conn.query("""
    SELECT TABLE_NAME, TABLE_TYPE, ROW_COUNT, COMMENT
    FROM CUST_DEMO_DB.INFORMATION_SCHEMA.TABLES
    WHERE TABLE_SCHEMA = 'CLUTCH_HORIZON'
    ORDER BY TABLE_TYPE, TABLE_NAME
""")
st.dataframe(df, use_container_width=True)
