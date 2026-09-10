# Masking Policies page
# Co-authored with CoCo
import streamlit as st

st.title("2. Tag-Based Masking Policies")

st.info("""
**Capability:** Attach a masking policy to a **tag** instead of individual columns. 
Every column with that tag — current and future — is automatically protected. 
Works across **all BI tools** querying Snowflake.

**Status:** GA
""")

st.markdown("""
### Why This Matters
When multiple BI tools query the same Snowflake tables, configuring masking 
per-tool is fragile and incomplete. Tag-based masking at the Snowflake layer ensures 
consistent protection regardless of which tool (or AI pipeline) reads the data.

### What We'll Demonstrate
1. Create a masking policy for STRING columns
2. Attach it to the `SNOWFLAKE.CORE.SEMANTIC_CATEGORY` system tag
3. Query as an authorized role — see full data
4. Query as a restricted role — see masked data
5. Show that new columns are auto-protected

### Outcome
One policy definition protects **every classified column** across all tables. 
No per-column configuration. No per-tool setup. New tables and columns are 
protected the moment they're created.
""")

st.divider()
st.subheader("Live Demo: Role-Based Masking")

conn = st.session_state["conn"]
S = st.session_state["SCHEMA"]

st.markdown("**As ACCOUNTADMIN (authorized):**")
df_full = conn.query(f"""
    SELECT customer_id, first_name, last_name, email, phone_number, sin_number, city, province
    FROM {S}.RAW_CUSTOMERS LIMIT 5
""")
st.dataframe(df_full, use_container_width=True)

st.markdown("**What PUBLIC role would see (simulated mask):**")
import pandas as pd
df_masked = df_full.copy()
for col in ["FIRST_NAME", "LAST_NAME", "EMAIL", "PHONE_NUMBER", "SIN_NUMBER"]:
    if col in df_masked.columns:
        df_masked[col] = "*** MASKED ***"
st.dataframe(df_masked, use_container_width=True)

st.divider()
st.subheader("Step-by-Step Instructions")
st.markdown("""
```sql
-- Step 1: Create masking policy
CREATE OR REPLACE MASKING POLICY CUST_DEMO_DB.CLUTCH_HORIZON.PII_STRING_MASK
  AS (val STRING) RETURNS STRING ->
  CASE
    WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN', 'SYSADMIN') THEN val
    ELSE '*** MASKED ***'
  END;

-- Step 2: Attach policy to the system classification tag
ALTER TAG SNOWFLAKE.CORE.SEMANTIC_CATEGORY
  SET MASKING POLICY CUST_DEMO_DB.CLUTCH_HORIZON.PII_STRING_MASK;

-- Step 3: Query as authorized role — full data
USE ROLE ACCOUNTADMIN;
SELECT * FROM CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS LIMIT 5;

-- Step 4: Query as restricted role — masked data
USE ROLE PUBLIC;
SELECT * FROM CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS LIMIT 5;

-- Step 5: CLEANUP (remove policy from tag after demo)
USE ROLE ACCOUNTADMIN;
ALTER TAG SNOWFLAKE.CORE.SEMANTIC_CATEGORY
  UNSET MASKING POLICY CUST_DEMO_DB.CLUTCH_HORIZON.PII_STRING_MASK;
```

**Key point to remember:** When your next BI tool connects to Snowflake, or your next 
dbt model creates a new table, the protection is already there. You never have to 
remember to add it.
""")

st.divider()
with st.expander("Real-World Use Cases at Clutch"):
    st.markdown("""
    | Use Case | Impact |
    |----------|--------|
    | **Protect SINs from support agents** who only need vehicle info | Support team sees `*** MASKED ***` for SIN_NUMBER but full vehicle details |
    | **Partial-mask emails for marketing analytics** | Marketing sees `*****@gmail.com` — enough for domain analysis, not enough to identify individuals |
    | **Mask financing data from BI-only roles** | Looker and Metabase users see sales totals but not individual credit card numbers or financing terms |
    | **Auto-protect new columns** | When dbt creates a new table with a `phone_number` column, it's masked instantly via the tag — no manual step |
    | **Consistent masking across 4 BI tools** | Same data protection whether the query comes from Metabase, Qlik, Looker, Coefficient, or an AI agent |
    """)
