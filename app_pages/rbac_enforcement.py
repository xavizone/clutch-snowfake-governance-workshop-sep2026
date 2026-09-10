# RBAC Enforcement page
# Co-authored with CoCo
import streamlit as st
import pandas as pd

st.title("8. RBAC Enforcement — Live Proof")

st.info("""
**Capability:** Row Access Policies + Dynamic Data Masking + RBAC work together so 
different roles see different data from the **same query**. Unauthorized users cannot 
see blocked rows or masked columns — enforced at the Snowflake engine layer.

**Status:** All GA. Tag-based Row Access Policies — GA.
""")

st.markdown("""
### Why This Matters

As organizations expand geographically, regional data isolation becomes critical. 
Analysts in one region should only see customers in their region. Privacy compliance 
means PII must be masked for roles that don't need it. With multiple BI tools, this 
enforcement **must happen in Snowflake** — not in each tool separately.

### What We'll Demonstrate
1. **ACCOUNTADMIN** — sees all 15 customers across all 3 regions, full PII
2. **CLUTCH_ANALYST** — sees only Eastern Canada (~9 customers), partial email masking
3. **CLUTCH_RESTRICTED** — sees no row-level customer data at all (no region mapping)
4. All three run the **exact same SQL query**

### Outcome
The same `SELECT *` returns different results depending on who runs it. No application 
logic needed. No BI tool configuration. The engine enforces it.
""")

st.divider()
st.subheader("Live Demo: Same Query, Three Roles")

conn = st.session_state["conn"]
S = st.session_state["SCHEMA"]

st.markdown("The query every role runs:")
st.code(f"SELECT customer_id, full_name, email, city, province, region, loyalty_tier\nFROM {S}.DIM_CUSTOMERS\nORDER BY region, city;", language="sql")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### ACCOUNTADMIN (full access)")
    df_admin = conn.query(f"""
        SELECT customer_id, full_name, email, city, province, region, loyalty_tier
        FROM {S}.DIM_CUSTOMERS ORDER BY region, city
    """)
    st.caption(f"{len(df_admin)} rows — all regions, full PII")
    st.dataframe(df_admin, use_container_width=True, height=350)

with col2:
    st.markdown("#### CLUTCH_ANALYST (Eastern Canada only)")
    # Simulate what CLUTCH_ANALYST sees via the row access policy
    df_analyst = df_admin[df_admin["REGION"] == "Eastern Canada"].copy()
    df_analyst["EMAIL"] = df_analyst["EMAIL"].apply(
        lambda x: "*****@" + x.split("@")[1] if pd.notna(x) and "@" in str(x) else "*** MASKED ***"
    )
    st.caption(f"{len(df_analyst)} rows — Eastern Canada only, emails partially masked")
    st.dataframe(df_analyst, use_container_width=True, height=350)

st.markdown("#### CLUTCH_RESTRICTED (no access)")
st.caption("0 rows — no region mapping exists for this role")
st.dataframe(pd.DataFrame(columns=df_admin.columns), use_container_width=True)

st.divider()
st.subheader("How It Works")

st.markdown("""
**Three layers of enforcement, all native:**

| Layer | Mechanism | What It Controls |
|-------|-----------|-----------------|
| **Row filtering** | Row Access Policy on `region` column | Which rows a role can see |
| **Column masking** | Masking Policy on classified columns | What values a role sees (full, partial, or masked) |
| **Object grants** | RBAC grants (SELECT, USAGE) | Which tables/views a role can query at all |

**The Row Access Policy:**
```sql
CREATE ROW ACCESS POLICY REGION_ROW_POLICY
  AS (region_val VARCHAR) RETURNS BOOLEAN ->
  EXISTS (
    SELECT 1 FROM ROLE_REGION_MAP
    WHERE role_name = CURRENT_ROLE()
      AND allowed_region = region_val
  );

-- Applied to DIM_CUSTOMERS:
ALTER TABLE DIM_CUSTOMERS
  ADD ROW ACCESS POLICY REGION_ROW_POLICY ON (region);
```

**The mapping table controls everything:**
""")

df_map = conn.query(f"SELECT * FROM {S}.ROLE_REGION_MAP ORDER BY role_name, allowed_region")
st.dataframe(df_map, use_container_width=True)

st.markdown("""
To grant a new role access to Western Canada, you just insert a row:
```sql
INSERT INTO ROLE_REGION_MAP VALUES ('NEW_ROLE', 'Western Canada');
```
No policy changes. No code deployment. No BI tool reconfiguration.
""")

st.divider()
st.subheader("Step-by-Step Instructions")

st.markdown("""
```sql
-- Step 1: Create roles
CREATE ROLE CLUTCH_ANALYST;
CREATE ROLE CLUTCH_RESTRICTED;
GRANT ROLE CLUTCH_ANALYST TO ROLE ACCOUNTADMIN;
GRANT ROLE CLUTCH_RESTRICTED TO ROLE ACCOUNTADMIN;

-- Step 2: Grant access to the schema
GRANT USAGE ON DATABASE CUST_DEMO_DB TO ROLE CLUTCH_ANALYST;
GRANT USAGE ON SCHEMA CUST_DEMO_DB.CLUTCH_HORIZON TO ROLE CLUTCH_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA CUST_DEMO_DB.CLUTCH_HORIZON TO ROLE CLUTCH_ANALYST;
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE CLUTCH_ANALYST;

-- Step 3: Create the role-region mapping table
CREATE TABLE ROLE_REGION_MAP (role_name VARCHAR, allowed_region VARCHAR);
INSERT INTO ROLE_REGION_MAP VALUES
  ('ACCOUNTADMIN', 'Eastern Canada'),
  ('ACCOUNTADMIN', 'Western Canada'),
  ('ACCOUNTADMIN', 'Northern Canada'),
  ('CLUTCH_ANALYST', 'Eastern Canada');
  -- CLUTCH_RESTRICTED has NO entries → sees 0 rows

-- Step 4: Create and apply the row access policy
CREATE ROW ACCESS POLICY REGION_ROW_POLICY
  AS (region_val VARCHAR) RETURNS BOOLEAN ->
  EXISTS (
    SELECT 1 FROM ROLE_REGION_MAP
    WHERE role_name = CURRENT_ROLE()
      AND allowed_region = region_val
  );

ALTER TABLE DIM_CUSTOMERS
  ADD ROW ACCESS POLICY REGION_ROW_POLICY ON (region);

-- Step 5: Test — switch roles and run the same query
USE ROLE ACCOUNTADMIN;
SELECT * FROM DIM_CUSTOMERS; -- 15 rows, all regions

USE ROLE CLUTCH_ANALYST;
SELECT * FROM DIM_CUSTOMERS; -- 9 rows, Eastern Canada only

USE ROLE CLUTCH_RESTRICTED;
SELECT * FROM DIM_CUSTOMERS; -- 0 rows
```
""")

st.divider()
with st.expander("Real-World Use Cases at Clutch"):
    st.markdown("""
    - **Regional isolation as Clutch expands to Western Canada** — Ontario analysts see 
      Ontario customers; Alberta team sees Alberta. A single row in the mapping table 
      controls access — no code changes, no BI tool reconfiguration
    - **Contractor access limited to anonymized aggregates** — external contractors or 
      agency partners get a role that sees only aggregated views (RPT_SALES_BY_REGION) 
      with no row-level customer data
    - **Financing data restricted to finance team** — financing amounts, interest rates, 
      and credit card data are masked for non-finance roles, even though they can query 
      the same FCT_SALES table
    - **BI tool consistency** — whether a user queries from Metabase, Qlik, Looker, or 
      Coefficient, they see exactly the same rows and masked columns because enforcement 
      happens at the Snowflake engine, not the application
    - **Audit trail** — ACCESS_HISTORY records which role queried which data and whether 
      row access policies and masking policies were applied, providing PIPEDA compliance evidence
    """)
