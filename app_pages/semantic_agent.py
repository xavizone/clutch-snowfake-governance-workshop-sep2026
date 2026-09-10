# Semantic Layer + Cortex Agent page
# Co-authored with CoCo
import streamlit as st

st.title("7. Semantic Layer + Cortex Agent")

st.info("""
**Capability:** Define business metrics once in a **Semantic View** and serve them 
consistently to every BI tool and AI agent. Create a **Cortex Agent** that answers 
business questions in natural language using the governed semantic model.

**Edition:** Standard+ | **Status:** Semantic Views — GA. Cortex Agents — GA. CoWork — GA.
""")

st.markdown("""
### Why This Matters

When multiple BI tools query the same warehouse with no shared metric definitions, numbers 
diverge. One tool calculates "revenue" differently from another. A semantic view defines 
metrics once — **every tool and every AI agent uses the same definition**.

### What We'll Demonstrate
1. A Semantic View on sales data with metrics, dimensions, and relationships
2. Query the semantic view using the `SEMANTIC_VIEW()` SQL construct
3. How Autopilot creates semantic views from Power BI (.pbit) or Tableau (.twbx) files
4. Create a Cortex Agent and use it in **Snowflake CoWork**

### Outcome
One governed semantic layer that eliminates metric inconsistency, enables natural 
language queries for non-technical stakeholders, and provides the foundation for 
AI-powered analytics.
""")

st.divider()
st.subheader("Live Demo: Query the Semantic View")

conn = st.session_state["conn"]

query_choice = st.selectbox("Choose a business question:", [
    "Total revenue by region and payment method",
    "Number of sales by vehicle make",
    "Average sale price by salesperson",
    "Revenue by customer loyalty tier",
])

queries = {
    "Total revenue by region and payment method": """SELECT * FROM SEMANTIC_VIEW(
    CUST_DEMO_DB.CLUTCH_HORIZON.SV_CLUTCH_SALES
    DIMENSIONS customers.customer_region, sales.payment_type
    METRICS sales.total_revenue, sales.num_sales
) ORDER BY TOTAL_REVENUE DESC""",
    "Number of sales by vehicle make": """SELECT * FROM SEMANTIC_VIEW(
    CUST_DEMO_DB.CLUTCH_HORIZON.SV_CLUTCH_SALES
    DIMENSIONS vehicles.vehicle_make
    METRICS sales.num_sales, sales.total_revenue, sales.average_sale_price
) ORDER BY NUM_SALES DESC""",
    "Average sale price by salesperson": """SELECT * FROM SEMANTIC_VIEW(
    CUST_DEMO_DB.CLUTCH_HORIZON.SV_CLUTCH_SALES
    DIMENSIONS sales.sales_rep
    METRICS sales.num_sales, sales.total_revenue, sales.average_sale_price
) ORDER BY TOTAL_REVENUE DESC""",
    "Revenue by customer loyalty tier": """SELECT * FROM SEMANTIC_VIEW(
    CUST_DEMO_DB.CLUTCH_HORIZON.SV_CLUTCH_SALES
    DIMENSIONS customers.tier
    METRICS sales.total_revenue, sales.num_sales, sales.average_sale_price
) ORDER BY TOTAL_REVENUE DESC""",
}

sql = queries[query_choice]
if st.button("Run Semantic Query", type="primary"):
    with st.spinner("Querying semantic view..."):
        df = conn.query(sql)
        st.dataframe(df, use_container_width=True)

with st.expander("View query"):
    st.code(sql, language="sql")

st.divider()
st.subheader("Using Your Agent in Snowflake CoWork")

st.markdown("""
**Snowflake CoWork** is a ready-to-use conversational interface that lets business users 
interact with data using natural language. When you create a Cortex Agent with a Semantic View, 
it becomes available in CoWork — enabling non-technical users to get answers without SQL.

#### What CoWork Means for Your Team

| Role | Without CoWork | With CoWork |
|------|---------------|-------------|
| **RevOps Manager** | Submits a ticket to the data team, waits days | Asks "What's our financing rate by province?" and gets an answer in seconds |
| **Salesperson** | Relies on weekly static reports | Asks "How am I performing vs other reps this quarter?" in real time |
| **Finance Director** | Exports data to Excel for analysis | Asks "Show me total revenue by payment method for Q3" and gets a chart |
| **CEO** | Waits for the data team to build a dashboard | Asks "What are our top 5 vehicle makes by revenue?" directly |

#### Steps to Use CoWork

1. **Create the agent** (already done in this lab):
```sql
CREATE OR REPLACE CORTEX AGENT CUST_DEMO_DB.CLUTCH_HORIZON.CLUTCH_SALES_AGENT
  COMMENT = 'Clutch sales analytics agent'
  TOOLS = (CUST_DEMO_DB.CLUTCH_HORIZON.SV_CLUTCH_SALES);
```

2. **Open CoWork** in Snowsight:
   - Navigate: **AI & ML > Agents**
   - Select **CLUTCH_SALES_AGENT** from the list
   - Or navigate directly to **Snowflake CoWork** from the left navigation

3. **Ask a question** in natural language:
   - "What is our total revenue by region?"
   - "Which salesperson has the highest average deal size?"
   - "How does financing vs full payment break down by province?"
   - "Show me a trend of sales over the last 6 months"

4. **Use Deep Research** for complex questions:
   - Click the `+` button in the message bar > select **Deep Research**
   - Ask: "Why are Western Canada sales lower than Eastern Canada? What factors contribute?"
   - CoWork decomposes the question, runs multiple analyses, and synthesizes a structured report

5. **Share insights** with your team:
   - Charts and tables generated by CoWork are saved as **Artifacts**
   - You can revisit, share, and reference them without regenerating
   - Set up **Automations** to re-run a question on a schedule and email the results

**Key point to remember:** CoWork inherits all Snowflake governance — row access policies, 
masking policies, and RBAC. A RevOps user asking CoWork a question sees only the data their 
role allows, automatically. No separate governance configuration for AI.
""")

st.divider()
st.subheader("Autopilot: Import from Power BI / Tableau")

st.markdown("""
**Instead of writing SQL**, you can create semantic views from existing BI models:

1. Navigate: **Workspaces > Add new > Semantic View**
2. Autopilot wizard opens — choose one:
   - **CoCo** — conversational creation guided by AI
   - **Upload Power BI** (.pbit or .pbix) — preserves DAX measures, relationships, calculated columns
   - **Upload Tableau** (.twb, .twbx, .tds, .tdsx) — preserves calculated fields and relationships
   - **Upload YAML** — for version-controlled definitions
3. Autopilot generates the semantic view automatically
4. Refine in **Semantic Studio** (the authoring environment in Workspaces)

**What Power BI ingestion preserves:**
- Table relationships → Semantic View relationships
- DAX measures → Semantic View metrics
- Calculated columns → Semantic View dimensions
- Renamed columns from M query → honored
- Primary keys → auto-detected (including composite)
""")

st.divider()
st.subheader("Step-by-Step Instructions")

st.markdown("""
```sql
-- Create a Semantic View with SQL
CREATE OR REPLACE SEMANTIC VIEW CUST_DEMO_DB.CLUTCH_HORIZON.SV_CLUTCH_SALES
  TABLES (
    customers AS CUST_DEMO_DB.CLUTCH_HORIZON.DIM_CUSTOMERS PRIMARY KEY (customer_id),
    vehicles AS CUST_DEMO_DB.CLUTCH_HORIZON.STG_VEHICLES PRIMARY KEY (vehicle_id),
    sales AS CUST_DEMO_DB.CLUTCH_HORIZON.FCT_SALES PRIMARY KEY (transaction_id)
  )
  RELATIONSHIPS (
    sales_to_customers AS sales (customer_id) REFERENCES customers,
    sales_to_vehicles AS sales (vehicle_id) REFERENCES vehicles
  )
  DIMENSIONS (
    customers.customer_region AS region,
    vehicles.vehicle_make AS make,
    sales.sales_rep AS salesperson,
    sales.sale_date AS transaction_date
  )
  METRICS (
    sales.total_revenue AS SUM(sales.sale_amount),
    sales.num_sales AS COUNT(transaction_id)
  )
  COMMENT = 'Vehicle marketplace analytics';

-- Create a Cortex Agent
CREATE OR REPLACE CORTEX AGENT CUST_DEMO_DB.CLUTCH_HORIZON.CLUTCH_SALES_AGENT
  TOOLS = (CUST_DEMO_DB.CLUTCH_HORIZON.SV_CLUTCH_SALES);

-- Then open CoWork: AI & ML > Agents > CLUTCH_SALES_AGENT
```
""")

st.divider()
with st.expander("Real-World Use Cases at Clutch"):
    st.markdown("""
    | Use Case | Impact |
    |----------|--------|
    | **RevOps team asks "financing rate by province?"** in CoWork | Instant answer without SQL, without opening any of the 4 BI tools |
    | **Sales performance without SQL** | Each salesperson checks their own numbers in CoWork — self-serve, no dashboard building needed |
    | **Board-ready KPIs from natural language** | CEO asks "What's our revenue this quarter vs last?" — gets a chart they can share |
    | **Eliminate metric inconsistency** | "Revenue" means the same thing in Metabase, Qlik, Looker, Coefficient, and CoWork — defined once in the Semantic View |
    | **Import Power BI model** | If Clutch has an existing Power BI semantic model, Autopilot converts it to a Snowflake Semantic View — preserving all DAX measures |
    | **Automated weekly report** | Set up a CoWork Automation: "Email me the sales summary by region every Monday at 9am" |
    """)
