# Setup & Prerequisites page
# Co-authored with CoCo
import streamlit as st

st.title("Getting Started")

st.markdown("""
Welcome to the **Snowflake Horizon Context** hands-on lab. This guide walks you through 
every major governance capability in Snowflake — from sensitive data discovery to AI-powered 
analytics — using a realistic Canadian eCommerce dataset.

Before diving into the exercises, make sure your environment is ready.
""")

st.divider()
st.subheader("1. Get a Snowflake Account")

st.markdown("""
If you don't already have a Snowflake account, you can sign up for a **free 30-day 
Enterprise Edition trial** — no credit card required:

1. Go to [snowflake.com/en/data-cloud/overview/trial](https://signup.snowflake.com/)
2. Choose **Enterprise Edition** (required for most governance features in this lab)
3. Select your preferred cloud provider and region
4. Complete the sign-up — you'll receive an activation email within minutes

The trial includes **$400 in free credits**, which is more than enough for this entire lab.
""")

st.divider()
st.subheader("2. Edition Requirements")

st.markdown("""
Most Horizon governance features require **Enterprise Edition or higher**. Here's 
what each lab section needs:
""")

edition_data = [
    {"Section": "1. Classification", "Feature": "Sensitive Data Classification", "Edition": "Enterprise", "Notes": "Auto-discovery of PII, system tags"},
    {"Section": "2. Masking Policies", "Feature": "Dynamic Data Masking", "Edition": "Enterprise", "Notes": "Column-level masking, tag-based masking"},
    {"Section": "3. Data Lineage", "Feature": "Data Lineage (object + column)", "Edition": "Enterprise", "Notes": "GET_LINEAGE, Snowsight lineage graph"},
    {"Section": "4. Trust Center", "Feature": "Trust Center scanners", "Edition": "Standard+", "Notes": "Available on all editions; some scanners Enterprise"},
    {"Section": "5. Data Quality", "Feature": "Data Metric Functions (DMFs)", "Edition": "Enterprise", "Notes": "System + custom DMFs, monitoring dashboard"},
    {"Section": "6. AI Context Layer", "Feature": "Cortex Descriptions, AI Guardrails", "Edition": "Enterprise", "Notes": "Guardrails require Enterprise; descriptions work on all"},
    {"Section": "7. Semantic + Agent", "Feature": "Semantic Views, Cortex Agents", "Edition": "Standard+", "Notes": "Available on all editions"},
    {"Section": "8. RBAC Enforcement", "Feature": "Row Access Policies", "Edition": "Enterprise", "Notes": "Row-level security requires Enterprise"},
    {"Section": "9. CoCo Prompts", "Feature": "Snowflake CoCo (Cortex Code)", "Edition": "Standard+", "Notes": "Available on all editions"},
]

st.dataframe(edition_data, use_container_width=True, hide_index=True)

st.info("""
**Bottom line:** To complete all sections of this lab, use an **Enterprise Edition** account. 
A 30-day Enterprise trial works perfectly.
""")

st.divider()
st.subheader("3. Set Up the Demo Data")

st.markdown("""
Run the following SQL to create the demo schema and load sample data. This takes 
about 30 seconds. You need **ACCOUNTADMIN** or a role with `CREATE SCHEMA` on the 
target database.
""")

with st.expander("SQL Setup Script (click to expand)", expanded=False):
    st.code("""
-- ============================================================
-- HORIZON CONTEXT LAB — SETUP SCRIPT
-- Run this once before starting the lab exercises.
-- Requires: ACCOUNTADMIN or equivalent privileges
-- Time: ~30 seconds
-- ============================================================

USE ROLE ACCOUNTADMIN;
USE WAREHOUSE COMPUTE_WH;  -- or your preferred warehouse

-- Create the lab database and schema
CREATE DATABASE IF NOT EXISTS CUST_DEMO_DB;
CREATE SCHEMA IF NOT EXISTS CUST_DEMO_DB.CLUTCH_HORIZON
  COMMENT = 'Horizon Context hands-on lab — Canadian eCommerce dataset';

USE SCHEMA CUST_DEMO_DB.CLUTCH_HORIZON;

-- ============================================================
-- RAW LAYER: Source tables with PII
-- ============================================================

CREATE OR REPLACE TABLE RAW_CUSTOMERS (
    customer_id NUMBER AUTOINCREMENT START 1001,
    first_name VARCHAR(100), last_name VARCHAR(100),
    email VARCHAR(200), phone_number VARCHAR(20),
    date_of_birth DATE, sin_number VARCHAR(11),
    drivers_license VARCHAR(20), street_address VARCHAR(300),
    city VARCHAR(100), province VARCHAR(50), postal_code VARCHAR(10),
    registration_date DATE, loyalty_tier VARCHAR(20),
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

INSERT INTO RAW_CUSTOMERS (first_name, last_name, email, phone_number,
    date_of_birth, sin_number, drivers_license, street_address, city,
    province, postal_code, registration_date, loyalty_tier)
VALUES
  ('Ava','Chen','ava.chen@gmail.com','+1-416-555-0101','1988-03-15',
   '046-454-286','C1234-56789-80101','123 Queen St W','Toronto',
   'Ontario','M5H 2N2','2024-01-15','Gold'),
  ('Liam','Patel','liam.patel@hotmail.com','+1-647-555-0202','1992-07-22',
   '121-345-671','P9876-12345-70922','456 Bloor St E','Toronto',
   'Ontario','M4W 3L4','2024-03-10','Silver'),
  ('Sophie','Tremblay','sophie.t@outlook.com','+1-514-555-0303','1985-11-08',
   '287-654-329','T4567-89012-51108','789 Rue Sainte-Catherine','Montreal',
   'Quebec','H3B 1B5','2023-11-20','Gold'),
  ('Noah','Williams','noah.w@yahoo.ca','+1-604-555-0404','1995-01-30',
   '398-765-430','W2345-67890-50130','321 Robson St','Vancouver',
   'British Columbia','V6B 3K9','2024-06-01','Bronze'),
  ('Emma','Singh','emma.singh@gmail.com','+1-403-555-0505','1990-09-12',
   '534-876-542','S6789-01234-00912','654 Stephen Ave','Calgary',
   'Alberta','T2P 4J8','2024-02-28','Gold');
-- (15 total rows — see full script in the workspace for all records)

-- Repeat similar pattern for RAW_VEHICLES (15 rows),
-- RAW_TRANSACTIONS (9 rows), RAW_WARRANTY_CLAIMS (5 rows)

-- ============================================================
-- STAGING LAYER: Cleaning views
-- ============================================================
CREATE OR REPLACE VIEW STG_CUSTOMERS AS
SELECT *, DATEDIFF('year', date_of_birth, CURRENT_DATE()) AS age
FROM RAW_CUSTOMERS WHERE first_name IS NOT NULL;

-- ============================================================
-- DIMENSION / FACT LAYER: CTAS tables (creates lineage)
-- ============================================================
CREATE OR REPLACE TABLE DIM_CUSTOMERS AS
SELECT *, first_name || ' ' || last_name AS full_name,
  CASE WHEN province IN ('Ontario','Quebec','Nova Scotia') THEN 'Eastern Canada'
       WHEN province IN ('Alberta','British Columbia') THEN 'Western Canada'
       ELSE 'Northern Canada' END AS region
FROM STG_CUSTOMERS;

-- ============================================================
-- REPORTING LAYER: Views for dashboards
-- ============================================================
CREATE OR REPLACE VIEW RPT_CUSTOMER_SUMMARY AS
SELECT customer_id, full_name, email, city, province, region,
  loyalty_tier FROM DIM_CUSTOMERS;

-- ============================================================
-- VERIFICATION
-- ============================================================
SELECT 'Setup complete!' AS status,
  (SELECT COUNT(*) FROM RAW_CUSTOMERS) AS customers,
  (SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
   WHERE TABLE_SCHEMA = 'CLUTCH_HORIZON') AS total_objects;
""", language="sql")

st.divider()
st.subheader("4. Verify Your Setup")

conn = st.session_state.get("conn")
if conn:
    if st.button("Check Lab Environment", type="primary"):
        check_sql = """SELECT
    CURRENT_ROLE() AS current_role,
    CURRENT_WAREHOUSE() AS warehouse,
    CURRENT_ACCOUNT() AS account,
    (SELECT COUNT(*) FROM CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS) AS customer_rows,
    (SELECT COUNT(*) FROM CUST_DEMO_DB.INFORMATION_SCHEMA.TABLES
     WHERE TABLE_SCHEMA = 'CLUTCH_HORIZON') AS total_objects"""
        try:
            df = conn.query(check_sql)
            st.dataframe(df, use_container_width=True)
            with st.expander(":material/visibility: View query"):
                st.code(check_sql.strip(), language="sql")

            rows = int(df.iloc[0]["CUSTOMER_ROWS"])
            objects = int(df.iloc[0]["TOTAL_OBJECTS"])
            if rows >= 15 and objects >= 10:
                st.success("Your environment is ready. Proceed to Section 1!")
            else:
                st.warning(f"Found {rows} customer rows and {objects} objects. "
                           f"Expected 15+ rows and 10+ objects. Run the setup script above.")
        except Exception as e:
            st.error(f"Setup check failed: {e}")
            st.info("Run the setup SQL script above first, then try again.")
    with st.expander("View query"):
        st.code(CHECK_SQL, language="sql")

st.divider()
st.subheader("5. Key Points to Remember")

st.markdown("""
- **All governance policies are enforced at the Snowflake engine layer** — they apply 
  regardless of which tool queries the data (BI, AI, API, or direct SQL)
- **Enterprise Edition** unlocks the full governance feature set — classification, masking, 
  row access policies, lineage, and data quality monitoring
- **No external tools required** — everything in this lab is native to Snowflake
- **CoCo (Cortex Code)** can perform every step conversationally — see Section 9
- The demo data is Canadian to showcase PIPEDA-relevant classifications (SINs, 
  provincial driver's licenses, Canadian phone numbers)
""")

st.divider()
st.subheader("6. Cleanup / Reset Lab")

st.markdown("""
Need to start over? Run the cleanup script below to drop the demo schema and all 
its objects. Then re-run the setup script in Section 3 to start fresh.
""")

with st.expander("Cleanup SQL (click to expand)", expanded=False):
    st.code("""
-- ============================================================
-- HORIZON CONTEXT LAB — CLEANUP / RESET
-- Drops the demo schema and all objects inside it.
-- After running this, re-run the Setup Script (Section 3) to start fresh.
-- ============================================================

USE ROLE ACCOUNTADMIN;

-- Remove row access policy from DIM_CUSTOMERS first (required before drop)
ALTER TABLE CUST_DEMO_DB.CLUTCH_HORIZON.DIM_CUSTOMERS
  DROP ROW ACCESS POLICY IF EXISTS CUST_DEMO_DB.CLUTCH_HORIZON.REGION_ROW_POLICY;

-- Drop the entire demo schema (cascades to all objects)
DROP SCHEMA IF EXISTS CUST_DEMO_DB.CLUTCH_HORIZON CASCADE;

-- Drop demo roles (optional — only if you created them)
DROP ROLE IF EXISTS CLUTCH_ANALYST;
DROP ROLE IF EXISTS CLUTCH_RESTRICTED;

-- Verify cleanup
SELECT 'Cleanup complete — schema dropped' AS status;
""", language="sql")

st.warning("Running cleanup will **permanently delete** all demo objects. Make sure you want to start over.")
