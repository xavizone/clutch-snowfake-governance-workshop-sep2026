# Trust Center page
# Co-authored with CoCo
import streamlit as st

st.title("4. Trust Center")

st.info("""
**Capability:** Evaluate, monitor, and remediate security risks with automated scanners. 
CIS Benchmarks, Threat Intelligence, AI Security, and **one-click remediation** (GA Aug 2026).

**Edition:** Available on all editions. Some scanners may require Enterprise.

**Status:** GA (One-click remediation GA Aug 14, 2026 — NEW)
""")

st.markdown("""
### Why This Matters

Every Snowflake account should have continuous security monitoring. For organizations 
handling financial data or operating under privacy regulations like PIPEDA, security 
posture is a board-level concern. The **AI Security scanner** is particularly relevant 
if you're running Cortex AI agents or LLM workloads.

### What We'll Demonstrate
1. Trust Center Overview — security posture at a glance
2. CIS Benchmarks scanner — violations and remediation
3. **One-click remediation** — generate SQL, review plan, execute
4. AI Security scanner — monitor AI agent configs and guardrails
5. Threat Intelligence — anomalous logins, data exfiltration signals
6. Notification setup — email alerts for new findings

### Outcome
A concrete security score on your account with actionable remediation steps — 
not a theoretical assessment but real findings with generated SQL to fix them.
""")

st.divider()
st.subheader("Scanner Packages")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### Security Essentials")
    st.markdown("""
    - Enabled by **default**
    - Runs bi-weekly
    - MFA enforcement
    - Network policies
    - Snowflake-funded
    """)

with col2:
    st.markdown("#### CIS Benchmarks")
    st.markdown("""
    - Industry standard
    - On-demand scans
    - MFA gaps
    - Over-privileged roles
    - Inactive users (90d)
    - Task role checks
    """)

with col3:
    st.markdown("#### Threat Intelligence")
    st.markdown("""
    - Anomalous logins
    - Unrecognized IPs
    - Data exfiltration
    - High error rates
    - Vulnerable clients
    """)

with col4:
    st.markdown("#### AI Security")
    st.markdown("""
    - Cortex Agent configs
    - Runtime guardrails
    - AI-related violations
    - Prompt injection monitoring
    - Model access audit
    """)

st.divider()
st.subheader("Live Demo: Access History")

conn = st.session_state["conn"]

if st.button("Query Recent Access History", type="primary"):
    access_sql = """SELECT
    query_start_time,
    user_name,
    f.value:objectName::STRING AS object_accessed,
    f.value:objectDomain::STRING AS object_type
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY,
  LATERAL FLATTEN(input => direct_objects_accessed) f
WHERE query_start_time >= DATEADD('hour', -4, CURRENT_TIMESTAMP())
  AND f.value:objectName::STRING ILIKE '%CLUTCH_HORIZON%'
ORDER BY query_start_time DESC
LIMIT 20"""
    with st.spinner("Querying ACCESS_HISTORY..."):
        df = conn.query(access_sql)
        if len(df) > 0:
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No access history found for CLUTCH_HORIZON in the last 4 hours. Try running some queries first.")
    with st.expander(":material/visibility: View query"):
        st.code(access_sql, language="sql")

st.divider()
st.subheader("Step-by-Step Instructions")
st.markdown("""
**In Snowsight UI:**
1. Navigate: **Governance & Security > Trust Center**
2. Select a warehouse (e.g., `COMPUTE_WH`)
3. Go to **Scanner Packages** tab
4. Enable **CIS Benchmarks** > Click Enable > Continue
5. Click the refresh icon for an on-demand scan
6. Go to **Violations** tab after scan completes
7. Click any violation > read remediation guidance
8. Try **one-click remediation** on a low-risk finding
9. Enable **AI Security** scanner for Cortex monitoring

**SQL — Access History audit:**
```sql
-- Who accessed customer data in the last 7 days?
SELECT query_start_time, user_name, direct_objects_accessed
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE query_start_time >= DATEADD('day', -7, CURRENT_TIMESTAMP())
  AND ARRAY_SIZE(FILTER(direct_objects_accessed,
    o -> o:objectName::STRING ILIKE '%CUSTOMER%')) > 0
ORDER BY query_start_time DESC LIMIT 20;

-- Which masking policies were applied?
SELECT query_start_time, user_name, policies_referenced
FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE ARRAY_SIZE(policies_referenced) > 0
ORDER BY query_start_time DESC LIMIT 20;
```
""")

st.divider()
with st.expander("Real-World Use Cases at Clutch"):
    st.markdown("""
    - **CIS benchmark before SOC 2 audit** — run the scanner, export findings, and 
      demonstrate to auditors that security controls are continuously monitored
    - **AI Security scanner for Anthropic workloads** — as Clutch scales AI, monitor 
      Cortex Agent configurations, guardrail status, and AI-related violations in one place
    - **Anomaly detection on login patterns** — as the team grows and new hires join, 
      detect unusual login locations, failed auth attempts, and potential credential compromise
    - **One-click remediation for quick wins** — fix MFA gaps, over-privileged roles, and 
      inactive users directly from the Trust Center without writing SQL manually
    - **PIPEDA compliance evidence** — access history provides auditable proof of who 
      accessed customer financing data, when, and whether masking policies were applied
    """)
