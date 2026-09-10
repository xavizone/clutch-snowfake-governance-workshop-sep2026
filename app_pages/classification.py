# Classification page
# Co-authored with CoCo
import streamlit as st
import json

st.title("1. Sensitive Data Classification")

st.info("""
**Capability:** Snowflake automatically discovers and classifies sensitive data columns 
using 100+ native semantic categories — including Canadian-specific types like 
`CA_SOCIAL_INSURANCE_NUMBER`, `CA_DRIVERS_LICENSE`, `CA_PHONE_NUMBER`, and `VIN`.

**Edition:** Enterprise or higher | **Status:** GA (AI mode in Public Preview)
""")

st.markdown("""
### Why This Matters
Organizations handling customer PII (names, emails, SINs), vehicle data (VINs), and financing 
records need to know exactly where sensitive data lives across their Snowflake estate — and 
keep that inventory current as new tables are added. This is essential for **PIPEDA**, 
**GDPR**, and other privacy regulations.

### What We'll Demonstrate
1. Run `EXTRACT_SEMANTIC_CATEGORIES` on a customer table
2. See Snowflake auto-detect Canadian PII types with HIGH confidence
3. Apply classification tags to columns automatically
4. Verify tags are applied and queryable

### Outcome
In under 2 minutes, you'll have a complete inventory of every sensitive column 
in a table — automatically classified by type (IDENTIFIER, QUASI_IDENTIFIER, SENSITIVE) 
with Canadian-specific subcategories.
""")

st.divider()
st.subheader("Live Demo: Classify RAW_CUSTOMERS")

conn = st.session_state["conn"]
S = st.session_state["SCHEMA"]

CLASSIFY_SQL = f"SELECT EXTRACT_SEMANTIC_CATEGORIES('{S}.RAW_CUSTOMERS')"

if st.button("Run EXTRACT_SEMANTIC_CATEGORIES", type="primary"):
    with st.spinner("Classifying..."):
        result = conn.query(CLASSIFY_SQL)
        raw = result.iloc[0, 0]
        parsed = json.loads(raw)
        
        st.success(f"Classification complete — {len(parsed)} columns analyzed")
        
        findings = []
        for col_name, info in sorted(parsed.items()):
            rec = info.get("recommendation", {})
            if rec:
                findings.append({
                    "Column": col_name,
                    "Semantic Category": rec.get("semantic_category", "—"),
                    "Privacy Category": rec.get("privacy_category", "—"),
                    "Confidence": rec.get("confidence", "—"),
                    "Coverage": f"{rec.get('coverage', 0):.0%}",
                    "Subcategory": (rec.get("details", [{}])[0].get("semantic_category", "—") 
                                   if rec.get("details") else "—")
                })
            else:
                findings.append({
                    "Column": col_name,
                    "Semantic Category": "Not classified",
                    "Privacy Category": "—", "Confidence": "—",
                    "Coverage": "—", "Subcategory": "—"
                })
        
        st.dataframe(findings, use_container_width=True)

with st.expander("View query"):
    st.code(CLASSIFY_SQL, language="sql")

st.divider()
st.subheader("Step-by-Step Instructions")
st.markdown("""
```sql
-- Step 1: Run classification on any table
SELECT EXTRACT_SEMANTIC_CATEGORIES('CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS');

-- Step 2: Apply discovered tags automatically
CALL ASSOCIATE_SEMANTIC_CATEGORY_TAGS(
  'CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS',
  EXTRACT_SEMANTIC_CATEGORIES('CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS')
);

-- Step 3: Verify tags applied (SQL)
SELECT COLUMN_NAME, TAG_NAME, TAG_VALUE
FROM TABLE(INFORMATION_SCHEMA.TAG_REFERENCES_ALL_COLUMNS(
  'CUST_DEMO_DB.CLUTCH_HORIZON.RAW_CUSTOMERS', 'TABLE'))
WHERE TAG_DATABASE = 'SNOWFLAKE' AND TAG_SCHEMA = 'CORE'
ORDER BY COLUMN_NAME;

-- Step 4: Set up automatic classification via Trust Center
-- Navigate: Governance & Security > Trust Center > Data Security
-- Click "Get started" to enable classification on a database
```
""")

st.divider()
st.subheader("Verify Tags in Snowsight (UI)")
st.markdown("""
After applying classification tags, you can verify them visually in Snowsight:

1. Navigate: **Catalog > Database Explorer**
2. Select **CUST_DEMO_DB > CLUTCH_HORIZON > RAW_CUSTOMERS**
3. Click the **Columns** tab
4. Look for **tag icons** next to classified columns (e.g., FIRST_NAME, EMAIL, SIN_NUMBER)
5. Hover over the tag icon to see the `SEMANTIC_CATEGORY` and `PRIVACY_CATEGORY` values
6. Navigate: **Governance & Security > Tags & Policies > Dashboard** to see account-wide 
   tagging coverage — how many columns are tagged vs untagged
""")

st.divider()
with st.expander("Real-World Use Cases at Clutch"):
    st.markdown("""
    | Use Case | Impact |
    |----------|--------|
    | **Auto-classify new vehicle listing tables** as they're created | New data is governed from day one — no manual tagging lag |
    | **Flag financing PII for PIPEDA audit** | When the privacy officer asks "which tables contain SINs?" — answer in seconds |
    | **Detect PII in warranty claim free text** | The `description` field in warranty claims contains embedded names, SINs, and VINs — classification catches it |
    | **Classify data before sending to Anthropic** | Know which columns are safe to include in LLM prompts and which need masking first |
    | **Onboard new data engineers faster** | Auto-generated classification gives new team members instant context on what's sensitive |
    """)
