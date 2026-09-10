# AI Context Layer page
# Co-authored with CoCo
import streamlit as st

st.title("6. AI Context Layer")

st.info("""
**Capability:** Cortex-powered auto-generated descriptions, Semantic Views (with 
Tableau/Power BI ingestion), AI Guardrails for prompt injection/jailbreak protection, 
and Model Registry with training data lineage.

**Edition:** Guardrails require Enterprise; descriptions available on all editions

**Status:** Cortex Descriptions — GA. Semantic Views — GA. AI Guardrails — GA. 
Snowflake-Provided Tags — **Public Preview Aug 2026** (NEW)
""")

st.markdown("""
### Why This Matters
As organizations adopt LLMs and AI agents, they need governed data pipelines that prevent 
PII from leaking into prompts, ensure consistent metric definitions, and provide the 
business context that makes AI answers accurate and trustworthy.

Semantic Views create governed, business-aligned definitions that both humans and 
AI agents consume — the foundation for reliable AI-powered analytics.

### What We'll Demonstrate
1. **Cortex Auto-Descriptions** — AI generates table/column docs from metadata + sample data
2. **Snowflake-Provided Tags** — out-of-the-box governance tags (NEW)
3. **AI Guardrails** — prompt injection and jailbreak protection
4. **Power BI/Tableau ingestion** — import existing BI semantic models into Snowflake

### Outcome
Every table and column is documented automatically. Business metrics are defined once 
in a Semantic View and consumed consistently by every BI tool and AI agent. AI workloads 
run under the same governance as human queries.
""")

st.divider()
st.subheader("Live Demo: AI-Generated Descriptions")

conn = st.session_state["conn"]
S = st.session_state["SCHEMA"]

st.markdown("**Current table comments (set from AI_GENERATE_TABLE_DESC):**")
DESC_SQL = f"""SELECT TABLE_NAME, COMMENT FROM CUST_DEMO_DB.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'CLUTCH_HORIZON' AND COMMENT IS NOT NULL AND COMMENT != ''
ORDER BY TABLE_NAME"""

df = conn.query(DESC_SQL)
st.dataframe(df, use_container_width=True)
with st.expander("View query"):
    st.code(DESC_SQL, language="sql")

st.markdown("**Tags applied to RAW_CUSTOMERS:**")
TAGS_SQL = f"""SELECT COLUMN_NAME, TAG_NAME, TAG_VALUE, TAG_DATABASE, TAG_SCHEMA
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS('{S}.RAW_CUSTOMERS', 'TABLE'))
ORDER BY COLUMN_NAME, TAG_NAME"""

df_tags = conn.query(TAGS_SQL)
if len(df_tags) > 0:
    st.dataframe(df_tags, use_container_width=True)
else:
    st.info("No tags found. Run classification first (Section 1).")
with st.expander("View query"):
    st.code(TAGS_SQL, language="sql")

st.divider()
st.subheader("Snowflake-Provided Tags (Public Preview Aug 2026)")

st.markdown("""
Snowflake now provides **out-of-the-box tags** in the `SNOWFLAKE.TAGS` schema — a consistent 
vocabulary for common governance use cases without creating and maintaining tags in each account:

| Tag | Purpose | How It Helps |
|-----|---------|-------------|
| `COST_CENTER` | Chargeback and cost allocation | Track which team or department owns compute costs for each table |
| `CERTIFICATION_STATUS` | Mark trusted production data | Distinguish production-ready tables from experimental/staging |
| `SENSITIVITY` | Data sensitivity classification | Label data as PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED |
| `ENVIRONMENT` | Dev/staging/production labels | Prevent accidental queries against production data from dev tools |
| `PROJECT` | Project-level grouping | Group tables by business initiative or project for cross-team visibility |
| `SKIP_TAG_PROPAGATION` | Control tag inheritance | Prevent tags from cascading to child objects when not appropriate |
""")

if st.button("List Snowflake-Provided Tags", type="primary"):
    try:
        df_sf_tags = conn.query("SHOW TAGS IN SCHEMA SNOWFLAKE.TAGS")
        st.dataframe(df_sf_tags[["name", "comment", "allowed_values"]], use_container_width=True)
    except Exception as e:
        st.warning(f"Could not list Snowflake-provided tags: {e}")
        st.info("Snowflake-Provided Tags are in Public Preview (Aug 2026). They may not be available in all accounts yet.")

with st.expander("View query"):
    st.code("SHOW TAGS IN SCHEMA SNOWFLAKE.TAGS;", language="sql")

st.markdown("""
**How these tags apply at Clutch:**
- **COST_CENTER**: With 4 BI tools consuming Snowflake, tag tables by owning team (Data, RevOps, Marketing) 
  to accurately charge back warehouse costs
- **CERTIFICATION_STATUS**: Mark `DIM_CUSTOMERS` and `FCT_SALES` as `CERTIFIED` so analysts and AI agents 
  know which tables are the authoritative source of truth
- **SENSITIVITY**: Label financing tables as `CONFIDENTIAL` and public vehicle listings as `PUBLIC` — 
  this feeds into tag-based masking policies automatically
- **ENVIRONMENT**: Prevent the data team from accidentally querying production data during development
""")

st.divider()
st.subheader("AI Guardrails")
st.markdown("""
Cortex AI Guardrails provide runtime protection for CoCo, CoWork, and Cortex Agents:

- **Prompt injection detection** — scans tool outputs for indirect injection attempts
- **Jailbreak prevention** — detects safety protocol bypass attempts
- **Zero-day protection** — identifies sophisticated unknown attack patterns

```sql
-- Enable AI Guardrails
ALTER ACCOUNT SET AI_SETTINGS = $$
  guardrails:
    advanced_prompt_injection:
      - enabled: true
$$;

-- Monitor guardrail activity
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.CORTEX_AI_GUARDRAILS_USAGE_HISTORY
WHERE GUARDRAILS_SIGNAL = TRUE
  AND USAGE_TIME >= DATEADD('hour', -72, CURRENT_TIMESTAMP())
LIMIT 100;
```
""")

st.divider()
st.subheader("Step-by-Step Instructions")
st.markdown("""
```sql
-- Generate AI descriptions for a table and its columns
CALL AI_GENERATE_TABLE_DESC(
  'CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS',
  {'describe_columns': true, 'use_table_data': true}
);

-- Save a description as a table comment
ALTER TABLE CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS
  SET COMMENT = 'Customer PII including names, SINs, and addresses. PIPEDA-regulated.';

-- Apply Snowflake-Provided Tags
ALTER TABLE CUST_DEMO_DB.CLUTCH_HORIZON.DIM_CUSTOMERS
  SET TAG SNOWFLAKE.TAGS.CERTIFICATION_STATUS = 'CERTIFIED';

ALTER TABLE CUST_DEMO_DB.CLUTCH_HORIZON.RAW_TRANSACTIONS
  SET TAG SNOWFLAKE.TAGS.SENSITIVITY = 'CONFIDENTIAL';

-- Create a Semantic View (via Snowsight Autopilot):
-- 1. Navigate: Workspaces > Add new > Semantic View
-- 2. Choose tables from CLUTCH_HORIZON
-- 3. Autopilot generates relationships, metrics, dimensions
-- 4. Import from Power BI (.pbit) or Tableau (.twbx) for existing models
```
""")

st.divider()
with st.expander("Real-World Use Cases at Clutch"):
    st.markdown("""
    | Use Case | Impact |
    |----------|--------|
    | **Auto-document all 4 BI tool source tables** | New analysts get instant context on every table without asking the data team |
    | **CERTIFICATION_STATUS on production tables** | AI agents and analysts know which tables are authoritative vs experimental |
    | **COST_CENTER for warehouse chargeback** | Accurately allocate Snowflake costs across RevOps, Marketing, and Data teams |
    | **SENSITIVITY tags feeding masking policies** | Tag a table as CONFIDENTIAL → masking policies auto-apply to all its classified columns |
    | **Cortex descriptions for new hire onboarding** | Generate column descriptions in bulk — a new analytics engineer understands the schema in minutes |
    | **AI Guardrails for Anthropic workloads** | Protect against prompt injection when AI agents query customer and financing data |
    """)
