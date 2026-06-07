import streamlit as st
import requests

st.set_page_config(page_title="LegalAI", page_icon="⚖️", layout="wide")
st.title("⚖️ LegalAI — Legal Document Summariser")
st.markdown("Upload any legal document — AI will summarise, classify clauses & score risk")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    st.success(f"✅ Selected: {uploaded_file.name}")
    
    if st.button("🔍 Analyse Document", type="primary"):
        with st.spinner("AI processing document..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                response = requests.post("http://localhost:8000/upload", files=files)
                data = response.json()
                
                if response.status_code == 200:
                    risk = data.get("risk", {})
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Risk Level", risk.get("level", "Low"))
                    with col2:
                        st.metric("Risk Score", f"{risk.get('score', 0):.1f}%")
                    with col3:
                        st.metric("File", data.get("filename", ""))
                    
                    st.divider()
                    st.subheader("📝 AI Summary")
                    st.write(data.get("summary", "No summary"))
                    
                    st.divider()
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("🔑 Key Points")
                        for pt in data.get("key_points", []):
                            st.markdown(f"• {pt}")
                    with col2:
                        st.subheader("👥 Entities Found")
                        ents = data.get("entities", {})
                        icons = {"parties": "👤", "dates": "📅", "locations": "📍", "organizations": "🏢", "money": "💰"}
                        for key, val in ents.items():
                            if val:
                                st.markdown(f"**{icons.get(key, '📌')} {key}:** {', '.join(val)}")
                    
                    st.divider()
                    st.subheader("🔍 Detected Clauses")
                    for clause in data.get("clauses", []):
                        color = "🔴" if clause.get("type") == "high_risk" else "🟡" if clause.get("type") == "medium_risk" else "🟢"
                        st.markdown(f"{color} **{clause.get('type', 'normal')}** — {clause.get('text', '')}")
                        
                else:
                    st.error(f"Error: {data.get('detail', 'Something went wrong')}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")