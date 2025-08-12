import streamlit as st
import pandas as pd
import io
import re

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

# ---- Setup ----
st.set_page_config(page_title="Azure Agent Chat", layout="wide")
st.title("🤖 Bookings Agent - l'agent qui crée vos pointages")

@st.cache_resource
def init_agent():
    client = AIProjectClient(
        credential=DefaultAzureCredential(),
        #endpoint="https://ai-foundry-test-01.services.ai.azure.com/api/projects/project",
        endpoint="https://agents-02.services.ai.azure.com/api/projects/agents02"
        # --- IGNORE ---
    )
    # agent = client.agents.get_agent("asst_r0ZZVg6KTwNJN7fqGW25cne5")
    agent = client.agents.get_agent("asst_yNkkFcW1ULGvxSaqmOR7Vu3A")
    return client, agent

client, agent = init_agent()

# ---- Session State ----
if "thread" not in st.session_state:
    st.session_state.thread = client.agents.threads.create()
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Display Chat History ----

# ---- Clear Session Button ----
if st.button("🧹 Clear Session"):
    st.session_state.messages = []
    st.session_state.thread = client.agents.threads.create()
    st.experimental_rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---- Chat Input ----
user_input = st.chat_input("Type your message here...")

if user_input:
    # Save + send user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    client.agents.messages.create(
        thread_id=st.session_state.thread.id,
        role="user",
        content=user_input
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Call the agent
    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            run = client.agents.runs.create_and_process(
                thread_id=st.session_state.thread.id,
                agent_id=agent.id
            )
            if run.status == "failed":
                st.error(f"Run failed: {run.last_error}")
            else:
                messages = list(client.agents.messages.list(
                    thread_id=st.session_state.thread.id,
                    order=ListSortOrder.ASCENDING
                ))

                last_agent_msg = next(
                    (m for m in reversed(messages) if m.role.value == "assistant"),
                    None
                )
                if last_agent_msg:
                    text = last_agent_msg.text_messages[-1].text.value
                    st.markdown(text)
                    st.session_state.messages.append({"role": "assistant", "content": text})

                    # Flexible mission parser: dynamically extract columns from named regex groups
                    def parse_missions(raw_text, pattern):
                        matches = list(pattern.finditer(raw_text))
                        data = []
                        for m in matches:
                            # Use all named groups found in the match
                            data.append({k: v.strip() if isinstance(v, str) else v for k, v in m.groupdict().items()})
                        return pd.DataFrame(data) if data else pd.DataFrame()

                    # Example: user can adjust the pattern to match their mission format
                    mission_pattern = re.compile(
                        r"(?P<date>[\d/:\s]+)\s*-\s*(?P<type>[^-]+?) for (?P<client>[^(]+)"
                        r"\((?P<department>[^)]+)\).*?Director: (?P<director>[^,]+), KAM: (?P<kam>[^.]+)\. Description: (?P<description>.+)"
                    )
                    df = parse_missions(text, mission_pattern)
                    if not df.empty:
                        st.subheader("📋 Missions Table")
                        st.dataframe(df)

                        # CSV download
                        csv = df.to_csv(index=False).encode("utf-8")
                        st.download_button(
                            label="📄 Download CSV",
                            data=csv,
                            file_name="missions.csv",
                            mime="text/csv"
                        )

                        # Excel download
                        excel_buffer = io.BytesIO()
                        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
                            df.to_excel(writer, index=False, sheet_name="Missions")
                            writer.close()

                        st.download_button(
                            label="📊 Download Excel",
                            data=excel_buffer.getvalue(),
                            file_name="missions.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )