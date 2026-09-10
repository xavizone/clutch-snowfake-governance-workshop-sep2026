# CoCo Prompts page — Governance Prompt Cookbook
# Co-authored with CoCo
import streamlit as st

st.title("9. Governance with CoCo Prompts")

st.info("""
**Capability:** Snowflake CoCo (Cortex Code) lets you configure governance policies 
in **natural language** — no SQL expertise required. Every capability we demoed in 
sections 1–8 can be done conversationally.

**Status:** GA. Intent-Driven Governance — **Public Preview Aug 2026** (NEW)
""")

st.markdown("""
### Why This Matters

Growing data teams need governance to be accessible to everyone — not just SQL experts. 
Not every team member will know the syntax for masking policies, row access policies, or 
Trust Center configuration. CoCo democratizes governance: any team member can assess, 
classify, protect, and audit data using natural language.

---

### How to Use These Prompts

Open **CoCo** in Snowsight (the AI assistant in the sidebar), paste any prompt below, 
and CoCo will generate the SQL, explain it, and execute after your approval.

---
""")

# Section 1: Classification
with st.expander("**1. Sensitive Data Classification**", expanded=False):
    st.markdown("""
    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Classify all tables in CUST_DEMO_DB.CLUTCH_HORIZON for sensitive data"* | Runs `EXTRACT_SEMANTIC_CATEGORIES` on each table, shows findings |
    | *"What sensitive data exists in my RAW_CUSTOMERS table?"* | Classifies the table and summarizes PII categories found |
    | *"Set up automatic classification on the CUST_DEMO_DB database"* | Guides you through Trust Center > Data Security setup |
    | *"Create a custom classifier for vehicle VIN numbers"* | Creates a `CUSTOM_CLASSIFIER` with VIN regex pattern |
    | *"Apply classification tags to all columns in RAW_CUSTOMERS"* | Runs `ASSOCIATE_SEMANTIC_CATEGORY_TAGS` |

    **Equivalent SQL:**
    ```sql
    SELECT EXTRACT_SEMANTIC_CATEGORIES('CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS');
    CALL ASSOCIATE_SEMANTIC_CATEGORY_TAGS(
      'CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS',
      EXTRACT_SEMANTIC_CATEGORIES('CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS')
    );
    ```
    """)

# Section 2: Masking
with st.expander("**2. Masking Policies**", expanded=False):
    st.markdown("""
    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Create a masking policy that hides PII from non-analyst roles"* | Generates `CREATE MASKING POLICY` with role-based CASE logic |
    | *"Apply masking to all classified columns using tag-based masking"* | Attaches policy to `SNOWFLAKE.CORE.SEMANTIC_CATEGORY` tag |
    | *"Show me a partial email mask that keeps the domain visible"* | Creates policy with `REGEXP_REPLACE` keeping `@domain.com` |
    | *"What columns are currently masked in CLUTCH_HORIZON?"* | Queries `INFORMATION_SCHEMA.POLICY_REFERENCES` |
    | *"Remove the masking policy from the SEMANTIC_CATEGORY tag"* | Runs `ALTER TAG ... UNSET MASKING POLICY` |

    **Equivalent SQL:**
    ```sql
    CREATE MASKING POLICY pii_string_mask AS (val STRING) RETURNS STRING ->
      CASE WHEN CURRENT_ROLE() IN ('ACCOUNTADMIN') THEN val
           ELSE '*** MASKED ***' END;
    ALTER TAG SNOWFLAKE.CORE.SEMANTIC_CATEGORY
      SET MASKING POLICY pii_string_mask;
    ```
    """)

# Section 3: Lineage
with st.expander("**3. Data Lineage**", expanded=False):
    st.markdown("""
    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Show me upstream lineage for RPT_CUSTOMER_SUMMARY"* | Runs `GET_LINEAGE` and displays the dependency chain |
    | *"What tables feed into FCT_SALES?"* | Traces upstream lineage for the fact table |
    | *"Where does the customer_email column come from?"* | Runs column-level lineage with `GET_LINEAGE` on the column |
    | *"Are there any tag gaps in my lineage chain?"* | Checks for missing tags on downstream columns |
    | *"Set up external lineage for our dbt project"* | Provides the OpenLineage endpoint + dbt-ol configuration |

    **Equivalent SQL:**
    ```sql
    SELECT * FROM TABLE(SNOWFLAKE.CORE.GET_LINEAGE(
        'CUST_DEMO_DB.CLUTCH_HORIZON.RPT_CUSTOMER_SUMMARY',
        'TABLE', 'UPSTREAM', 5));
    ```
    """)

# Section 4: Trust Center
with st.expander("**4. Trust Center & Security**", expanded=False):
    st.markdown("""
    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Run a CIS benchmark scan and show me critical violations"* | Guides Trust Center enablement, runs scan, shows violations |
    | *"Enable the AI Security scanner"* | Walks through enabling the scanner package |
    | *"Who accessed customer data in the last 7 days?"* | Queries `ACCESS_HISTORY` with object filter |
    | *"Show me users who haven't logged in for 90 days"* | Queries Trust Center violations or `USERS` view |
    | *"Enable AI Guardrails for prompt injection protection"* | Generates `ALTER ACCOUNT SET AI_SETTINGS` SQL |

    **Equivalent SQL:**
    ```sql
    ALTER ACCOUNT SET AI_SETTINGS = $$
      guardrails:
        advanced_prompt_injection:
          - enabled: true
    $$;
    ```
    """)

# Section 5: Data Quality
with st.expander("**5. Data Quality**", expanded=False):
    st.markdown("""
    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Set up NULL checks on the email column of RAW_CUSTOMERS"* | Attaches `SNOWFLAKE.CORE.NULL_COUNT` DMF |
    | *"Create a VIN format validator"* | Creates a custom DMF with VIN regex validation |
    | *"Show me data quality violations in CLUTCH_HORIZON"* | Queries DMF results and violation history |
    | *"Find the actual rows with NULL emails"* | Runs `SYSTEM$DATA_METRIC_SCAN` |
    | *"Set up data quality monitoring for the entire schema"* | Attaches DMFs at schema level |

    **Equivalent SQL:**
    ```sql
    ALTER TABLE RAW_CUSTOMERS ADD DATA METRIC FUNCTION
      SNOWFLAKE.CORE.NULL_COUNT ON (email);
    ```
    """)

# Section 6: AI Context
with st.expander("**6. AI Context & Descriptions**", expanded=False):
    st.markdown("""
    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Generate descriptions for all tables in CLUTCH_HORIZON"* | Runs `AI_GENERATE_TABLE_DESC` on each table |
    | *"Describe the RAW_CUSTOMERS table and all its columns"* | Generates and optionally saves descriptions as comments |
    | *"What Snowflake-provided tags are available?"* | Lists tags in `SNOWFLAKE.TAGS` schema (PuPr Aug 2026) |
    | *"Tag RAW_CUSTOMERS with DATA_DOMAIN = CUSTOMER"* | Runs `ALTER TABLE ... SET TAG` |

    **Equivalent SQL:**
    ```sql
    CALL AI_GENERATE_TABLE_DESC('CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS',
      {'describe_columns': true, 'use_table_data': true});
    ```
    """)

# Section 7: Semantic Layer
with st.expander("**7. Semantic Layer & Agent**", expanded=False):
    st.markdown("""
    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Create a semantic view for our sales data"* | Guides through Autopilot or generates `CREATE SEMANTIC VIEW` SQL |
    | *"Build a Cortex Agent using the SV_CLUTCH_SALES semantic view"* | Generates `CREATE CORTEX AGENT` SQL |
    | *"Import our Power BI model into a semantic view"* | Walks through Autopilot > Upload Power BI flow |
    | *"What metrics are defined in SV_CLUTCH_SALES?"* | Runs `SHOW SEMANTIC METRICS` |
    | *"Query total revenue by region from the semantic view"* | Generates `SEMANTIC_VIEW()` SQL |

    **Equivalent SQL:**
    ```sql
    CREATE CORTEX AGENT CLUTCH_SALES_AGENT
      TOOLS = (CUST_DEMO_DB.CLUTCH_HORIZON.SV_CLUTCH_SALES);
    ```
    """)

# Section 8: RBAC
with st.expander("**8. RBAC & Access Control**", expanded=False):
    st.markdown("""
    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Create a row access policy that restricts customer data by region"* | Generates RAP SQL + mapping table |
    | *"Show me what the CLUTCH_ANALYST role can see vs ACCOUNTADMIN"* | Compares row counts and visible columns |
    | *"Create a role that can only see Eastern Canada customers"* | Creates role, grants, and mapping table entry |
    | *"Which policies are applied to DIM_CUSTOMERS?"* | Queries policy references for the table |
    | *"Explain the privileges needed for CLUTCH_ANALYST to query this schema"* | Lists required USAGE + SELECT grants |

    **Equivalent SQL:**
    ```sql
    CREATE ROW ACCESS POLICY REGION_ROW_POLICY
      AS (region_val VARCHAR) RETURNS BOOLEAN ->
      EXISTS (SELECT 1 FROM ROLE_REGION_MAP
              WHERE role_name = CURRENT_ROLE()
                AND allowed_region = region_val);
    ```
    """)

# Section 9: Intent-Driven Governance
with st.expander("**9. Intent-Driven Governance (PuPr Aug 2026)**", expanded=True):
    st.markdown("""
    **The ultimate CoCo governance workflow** — assess, plan, and apply governance 
    controls in a single conversational session:

    | Prompt | What CoCo Does |
    |--------|---------------|
    | *"Assess my governance posture for CUST_DEMO_DB"* | Scans classification coverage, masking gaps, tag completeness |
    | *"Apply classification, tagging, and masking to CLUTCH_HORIZON in one workflow"* | Orchestrates classify → tag → mask → verify as a governed change plan |
    | *"Show me what governance controls are missing in this schema"* | Identifies unclassified tables, unmasked PII, missing row policies |
    | *"Generate a governance plan for PIPEDA compliance"* | Creates a prioritized remediation plan with SQL |
    | *"Review and approve the governance changes before applying"* | Shows the SQL plan, waits for your approval before executing |

    **This is the "one prompt to rule them all" approach:**
    
    > *"I want to make sure CLUTCH_HORIZON is PIPEDA compliant. 
    > Classify all sensitive data, apply appropriate masking policies, 
    > set up row access for regional isolation, and enable Trust Center monitoring. 
    > Show me the plan before executing anything."*
    
    CoCo will:
    1. Scan all tables for sensitive data
    2. Generate classification tags
    3. Create masking policies for each data type
    4. Propose row access policies based on your role structure
    5. Enable Trust Center scanners
    6. **Present the full plan for your review**
    7. Execute only after your explicit approval
    """)

st.divider()
st.markdown("""
### Key Takeaway

Every SQL command shown in sections 1–8 can be replaced with a CoCo prompt. 
For growing data teams, this means:

- **New hires** can implement governance on day one — no SQL mastery required
- **Data stewards** can audit and remediate without engineering support
- **Compliance officers** can verify privacy controls conversationally
- **Data leaders** can assess the entire governance posture in one question
""")
