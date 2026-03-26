import streamlit as st
import google.generativeai as genai
import PyPDF2
import io

st.set_page_config(page_title="AI Research Assistant", page_icon="🤖", layout="wide")

st.title("🤖 AI Research Assistant")
st.markdown("Upload PDFs and ask questions - Powered by Google Gemini AI")

# Initialize Gemini
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    st.sidebar.success("✅ AI Ready!")
except:
    model = None
    st.sidebar.error("❌ Add GOOGLE_API_KEY to secrets")

# Session state
if "papers" not in st.session_state:
    st.session_state.papers = {}
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("📤 Upload PDF")
    uploaded = st.file_uploader("Choose a PDF", type=["pdf"])
    
    if uploaded and model:
        if st.button("Process"):
            try:
                reader = PyPDF2.PdfReader(io.BytesIO(uploaded.read()))
                text = ""
                for page in reader.pages[:8]:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
                if text:
                    st.session_state.papers[uploaded.name] = text[:4000]
                    st.success(f"✅ {uploaded.name}")
                else:
                    st.error("No text found")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    st.markdown("---")
    st.subheader("📚 Your Papers")
    for name in list(st.session_state.papers.keys()):
        col1, col2 = st.columns([3,1])
        with col1:
            st.write(name[:30])
        with col2:
            if st.button("❌", key=name):
                del st.session_state.papers[name]
                st.rerun()
    
    st.markdown("---")
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat display
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**You:** {msg['content']}")
    else:
        st.markdown(f"**🤖:** {msg['content']}")

# Input
st.markdown("---")
q = st.text_input("Ask a question:")
if st.button("Send") and q and model:
    st.session_state.messages.append({"role": "user", "content": q})
    with st.spinner("Thinking..."):
        if st.session_state.papers:
            ctx = "\n\n".join([f"[{n}]\n{t[:600]}" for n, t in st.session_state.papers.items()])
            prompt = f"Papers:\n{ctx[:3000]}\n\nQuestion: {q}\nAnswer:"
            resp = model.generate_content(prompt)
            ans = resp.text
        else:
            ans = "No papers uploaded."
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()
elif q and not model:
    st.error("Add GOOGLE_API_KEY to secrets")