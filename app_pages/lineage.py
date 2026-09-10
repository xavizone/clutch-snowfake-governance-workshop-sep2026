# Lineage page
# Co-authored with CoCo
import streamlit as st

st.title("3. End-to-End Data Lineage")

st.info("""
**Capability:** Snowflake automatically tracks data flow from source to target — 
object-level and column-level. Includes lineage through stored procedures, tasks, 
and external tools (dbt, Airflow) via OpenLineage.

**Edition:** Enterprise or higher | **Status:** Native lineage — GA. External lineage — **GA Sep 2026**
""")

st.markdown("""
### Why This Matters

When using tools like **dbt** as a core transformation layer, lineage metadata is 
automatically generated in Snowflake — you may already have years of lineage data 
without knowing it. The key question for any audit: *"How long would it take to prove 
the lineage of a metric in your dashboard back to the raw source?"*

**Key insight:** If you use dbt, Snowflake Tasks, or stored procedures, lineage 
metadata is already being created automatically.

### What We'll Demonstrate
1. View the lineage graph in Snowsight (RAW → STG → DIM/FCT → RPT)
2. Trace column-level lineage (e.g., `customer_email` back to `RAW_CUSTOMERS.EMAIL`)
3. Use `GET_LINEAGE` for programmatic access
4. Show tag propagation through lineage chains
5. External lineage (OpenLineage REST endpoint for dbt/Airflow)

### Outcome
Complete source-to-dashboard traceability. Every metric can be traced back to its 
raw source in seconds, not weeks. Tags propagate through the lineage chain with 
one-click remediation for gaps.
""")

st.divider()
st.subheader("Live Demo: Programmatic Lineage")

conn = st.session_state["conn"]
S = st.session_state["SCHEMA"]

table_choice = st.selectbox("Select a table to trace lineage:", [
    "RPT_CUSTOMER_SUMMARY", "RPT_VEHICLE_RELIABILITY", "RPT_SALES_BY_REGION",
    "FCT_SALES", "DIM_CUSTOMERS"
])

direction = st.radio("Direction:", ["UPSTREAM", "DOWNSTREAM"], horizontal=True)

LINEAGE_SQL = f"""SELECT DISTANCE, SOURCE_OBJECT_NAME AS SOURCE, SOURCE_OBJECT_DOMAIN AS SRC_TYPE,
    TARGET_OBJECT_NAME AS TARGET, TARGET_OBJECT_DOMAIN AS TGT_TYPE
FROM TABLE(SNOWFLAKE.CORE.GET_LINEAGE('{S}.{table_choice}', 'TABLE', '{direction}', 5))
ORDER BY DISTANCE"""

if st.button("Get Lineage", type="primary"):
    with st.spinner("Tracing lineage..."):
        df = conn.query(LINEAGE_SQL)
        if len(df) > 0:
            st.dataframe(df, use_container_width=True)
            st.success(f"Found {len(df)} lineage relationships")
        else:
            st.warning("No lineage found in this direction.")

with st.expander("View query"):
    st.code(LINEAGE_SQL, language="sql")

st.divider()
st.subheader("Snowsight UI Walkthrough")
st.markdown("""
1. Navigate: **Catalog > Database Explorer**
2. Find `CUST_DEMO_DB.CLUTCH_HORIZON.RPT_CUSTOMER_SUMMARY`
3. Click the **Lineage** tab
4. Expand upstream nodes (click `+`)
5. Click a column > **View Lineage** > see column-level flow
6. Check for tag gap indicators (dashed border = missing tag)
7. Use **Review and Apply** to propagate tags in one click
""")

st.divider()
st.subheader("External Lineage with dbt (GA Sep 2026)")

st.markdown("""
Snowflake's **External Lineage** feature accepts **OpenLineage-compatible events** through a 
REST endpoint. This means tools like dbt and Airflow can send lineage metadata directly to 
Snowflake, where it appears in the same lineage graph as native Snowflake lineage.

**How it works:**

1. dbt runs a transformation (e.g., `dbt run`)
2. The OpenLineage integration captures the input/output tables and columns
3. An OpenLineage event is sent to Snowflake's REST endpoint
4. Snowflake incorporates it into the native lineage graph in Snowsight
5. External nodes appear labeled by vendor (e.g., "dbt", "Airflow")

**Setup steps:**

```bash
# 1. Install the OpenLineage-dbt integration
pip3 install openlineage-dbt

# 2. Configure transport (in your OpenLineage YAML config)
transport:
  type: http
  url: https://<your_account>.snowflakecomputing.com
  endpoint: /api/v2/lineage/external-lineage
  auth:
    type: api_key
    apiKey: <your_jwt_token>
  compression: gzip

# 3. Replace 'dbt run' with 'dbt-ol run'
dbt-ol run    # instead of: dbt run
dbt-ol build  # instead of: dbt build
```

```sql
-- Grant the integration user permission to send lineage
GRANT INGEST LINEAGE ON ACCOUNT TO ROLE dbt_lineage_role;

-- Grant access to referenced objects so Snowflake can resolve them
GRANT USAGE ON DATABASE my_db TO ROLE dbt_lineage_role;
GRANT SELECT ON ALL TABLES IN SCHEMA my_db.my_schema TO ROLE dbt_lineage_role;
```

**What you see in Snowsight:** External objects appear in the lineage graph with a vendor 
label. You can click them for details, trace column-level lineage through them, and the 
same tag propagation and gap detection works across external nodes.

**Also supported:** Apache Airflow (via `openlineage-airflow` package) and any tool with an 
OpenLineage integration. Column-level lineage is captured via the `columnLineage` facet.
""")

st.divider()
st.subheader("Step-by-Step Instructions")
st.markdown("""
```sql
-- Object-level lineage (upstream of a reporting view)
SELECT * FROM TABLE(SNOWFLAKE.CORE.GET_LINEAGE(
    'CUST_DEMO_DB.CLUTCH_HORIZON.RPT_CUSTOMER_SUMMARY',
    'TABLE', 'UPSTREAM', 5
));

-- Column-level lineage (where does customer_email come from?)
SELECT * FROM TABLE(SNOWFLAKE.CORE.GET_LINEAGE(
    'CUST_DEMO_DB.CLUTCH_HORIZON.FCT_SALES.CUSTOMER_EMAIL',
    'COLUMN', 'UPSTREAM', 5
));
```
""")

st.divider()
with st.expander("Real-World Use Cases at Clutch"):
    st.markdown("""
    | Use Case | Impact |
    |----------|--------|
    | **Trace the Clutch Certified Reliability Report** back to raw warranty claims | Prove to auditors exactly which source tables and columns feed the published report |
    | **Impact analysis before changing the vehicle pricing model** | Before modifying `list_price` in RAW_VEHICLES, see every downstream table and dashboard affected |
    | **Debug metric discrepancies across 4 BI tools** | When Metabase and Qlik show different revenue numbers, trace both back to the same source and find where they diverge |
    | **Onboard new analytics engineers** | New hires can visually understand the entire data pipeline in minutes instead of weeks of tribal knowledge |
    | **Connect dbt lineage to Snowflake** | With external lineage, dbt model dependencies appear in the same graph — one unified view of all data flow |
    | **Regulatory compliance (PIPEDA)** | Demonstrate data provenance for any metric — "where did this number come from?" has a one-click answer |
    """)
