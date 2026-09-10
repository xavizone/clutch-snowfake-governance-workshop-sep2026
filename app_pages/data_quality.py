# Data Quality page
# Co-authored with CoCo
import streamlit as st

st.title("5. Data Quality Monitoring")

st.info("""
**Capability:** Continuously validate data health with Data Metric Functions (DMFs) — 
system-provided and custom. Serverless execution, schema-level attachment, anomaly 
detection, and a centralized monitoring dashboard.

**Status:** DMFs — GA. Monitoring Dashboard — **Public Preview Jul 2026** (NEW)
""")

st.markdown("""
### Why This Matters
Whether you use external data quality tools or not, Snowflake's native DMFs offer a 
complementary layer that runs serverlessly inside Snowflake — no external tool 
needed, no data movement, and fully integrated with the governance UI.

### What We'll Demonstrate
1. System DMFs attached to customer data (NULL_COUNT, DUPLICATE_COUNT)
2. Custom DMF for VIN format validation (17-char alphanumeric, no I/O/Q)
3. `SYSTEM$DATA_METRIC_SCAN` to find the actual failing rows
4. Centralized data quality dashboard in Snowsight
5. Cortex-suggested quality checks (AI-powered)

### Outcome
Automated, scheduled quality checks that run inside Snowflake — catching NULL emails, 
duplicate records, and malformed VINs before they reach BI dashboards or AI pipelines.
""")

st.divider()
st.subheader("Live Demo: Data Quality Checks")

conn = st.session_state["conn"]
S = st.session_state["SCHEMA"]

st.markdown("**Attached DMFs on RAW_CUSTOMERS:**")
df_dmfs = conn.query(f"""
    SELECT 
        METRIC_DATABASE_NAME || '.' || METRIC_SCHEMA_NAME || '.' || METRIC_NAME AS dmf,
        REF_ENTITY_NAME AS on_table,
        PARSE_JSON(REF_ARGUMENTS)[0]:name::STRING AS on_column,
        SCHEDULE_STATUS
    FROM TABLE(CUST_DEMO_DB.INFORMATION_SCHEMA.DATA_METRIC_FUNCTION_REFERENCES(
        REF_ENTITY_NAME => '{S}.RAW_CUSTOMERS',
        REF_ENTITY_DOMAIN => 'TABLE'
    ))
""")
st.dataframe(df_dmfs, use_container_width=True)

st.markdown("**Custom VIN Validator DMF on RAW_VEHICLES:**")
df_vin = conn.query(f"""
    SELECT 
        METRIC_NAME AS dmf,
        REF_ENTITY_NAME AS on_table,
        PARSE_JSON(REF_ARGUMENTS)[0]:name::STRING AS on_column,
        SCHEDULE_STATUS
    FROM TABLE(CUST_DEMO_DB.INFORMATION_SCHEMA.DATA_METRIC_FUNCTION_REFERENCES(
        REF_ENTITY_NAME => '{S}.RAW_VEHICLES',
        REF_ENTITY_DOMAIN => 'TABLE'
    ))
""")
st.dataframe(df_vin, use_container_width=True)

st.markdown("**Quick validation — run VIN check now:**")
if st.button("Check VIN Format", type="primary"):
    df_check = conn.query(f"""
        SELECT VIN, LENGTH(VIN) AS vin_length,
            CASE 
                WHEN LENGTH(VIN) != 17 THEN 'Wrong length'
                WHEN VIN RLIKE '.*[IOQ].*' THEN 'Contains I/O/Q'
                WHEN NOT VIN RLIKE '^[A-HJ-NPR-Z0-9]{{17}}$' THEN 'Invalid chars'
                ELSE 'Valid'
            END AS status
        FROM {S}.RAW_VEHICLES
        ORDER BY status DESC
    """)
    st.dataframe(df_check, use_container_width=True)

st.divider()
st.subheader("Step-by-Step Instructions")
st.markdown("""
```sql
-- Attach system DMFs to a table
ALTER TABLE CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS
  SET DATA_METRIC_SCHEDULE = 'TRIGGER_ON_CHANGES';

ALTER TABLE CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS
  ADD DATA METRIC FUNCTION SNOWFLAKE.CORE.NULL_COUNT ON (email);

-- Create a custom DMF for VIN validation
CREATE OR REPLACE DATA METRIC FUNCTION 
  CUST_DEMO_DB.CLUTCH_HORIZON.INVALID_VIN_COUNT(
    ARG_T TABLE(ARG_C VARCHAR))
RETURNS NUMBER AS
$$
  SELECT COUNT_IF(
    LENGTH(ARG_C) != 17 OR ARG_C RLIKE '.*[IOQ].*'
    OR NOT ARG_C RLIKE '^[A-HJ-NPR-Z0-9]{17}$')
  FROM ARG_T
$$;

-- Attach to vehicles table
ALTER TABLE CUST_DEMO_DB.CLUTCH_HORIZON.RAW_VEHICLES
  ADD DATA METRIC FUNCTION 
    CUST_DEMO_DB.CLUTCH_HORIZON.INVALID_VIN_COUNT ON (vin);

-- Find the actual rows that failed
SELECT * FROM TABLE(SYSTEM$DATA_METRIC_SCAN(
    REF_ENTITY_NAME => 'CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS',
    METRIC_NAME => 'snowflake.core.null_count',
    ARGUMENT_NAME => 'EMAIL'
));

-- Centralized dashboard: Governance & Security > Data Quality
```
""")

st.divider()
with st.expander("Real-World Use Cases at Clutch"):
    st.markdown("""
    - **VIN format validation before listing vehicles** — the custom `INVALID_VIN_COUNT` DMF 
      catches malformed VINs (wrong length, invalid characters) before a vehicle goes live 
      on the marketplace, preventing downstream data issues
    - **NULL checks on required fields** — monitor email, phone, and SIN columns for NULLs 
      that could break customer communications or compliance reporting
    - **Freshness monitoring on RudderStack-loaded tables** — attach freshness DMFs to tables 
      populated by RudderStack (4.7M jobs) to alert if data stops flowing
    - **Duplicate detection on customer records** — `DUPLICATE_COUNT` on email catches 
      duplicate customer registrations that inflate marketing metrics
    - **Schema-level monitoring** — attach DMFs to the entire `CLUTCH_HORIZON` schema so 
      every new table automatically gets baseline quality checks
    """)
