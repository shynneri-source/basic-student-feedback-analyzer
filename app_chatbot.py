import streamlit as st
import pandas as pd
import json
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px

from analyzer import analyze_feedback, render_analysis

HISTORY_FILE = "history.json"

# ============================================================
# TODO 2: Caching
# ============================================================
@st.cache_data(max_entries=1000)
def cached_analyze(text: str):
    return analyze_feedback(text)

# ============================================================
# HÀM QUẢN LÝ LỊCH SỬ (TODO 11 & 7)
# ============================================================
def load_history(path: str = HISTORY_FILE) -> list[dict]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_history(history: list[dict], path: str = HISTORY_FILE):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def init_session_state():
    if "history" not in st.session_state:
        st.session_state.history = load_history()
    if "messages" not in st.session_state:
        st.session_state.messages = []
        for item in st.session_state.history:
            st.session_state.messages.append({"role": "user", "content": item["text"]})
            st.session_state.messages.append({"role": "assistant", "content": render_analysis(item)})

def delete_feedback(index: int):
    st.session_state.history.pop(index)
    save_history(st.session_state.history)
    st.session_state.messages = []
    for item in st.session_state.history:
        st.session_state.messages.append({"role": "user", "content": item["text"]})
        st.session_state.messages.append({"role": "assistant", "content": render_analysis(item)})
    st.rerun()

# ============================================================
# VISUALIZATION (TODO 5 & 6)
# ============================================================
def render_wordcloud(history: list[dict]):
    all_keywords = [kw for item in history for kw in item.get("keywords", [])]
    if not all_keywords:
        st.info("Chưa đủ dữ liệu từ khóa.")
        return
        
    text = " ".join(all_keywords)
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)

def render_sentiment_timeline(history: list[dict]):
    if not history:
        return
    df = pd.DataFrame(history)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    daily_sent = df.groupby(["date", "sentiment"]).size().reset_index(name="count")
    
    if not daily_sent.empty:
        fig = px.line(daily_sent, x="date", y="count", color="sentiment", title="Xu hướng cảm xúc theo thời gian")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# MAIN
# ============================================================
def main():
    st.set_page_config(page_title="Feedback Analyzer", page_icon="🤖", layout="wide")
    init_session_state()

    st.title("🤖 Chatbot Phân tích Phản hồi Sinh viên")

    # TODO 10: Hướng dẫn sử dụng
    with st.expander("ℹ️ Hướng dẫn sử dụng & Ý nghĩa chỉ số"):
        st.markdown("""
        - **Cảm xúc**: Mức độ thái độ (Tích cực 😊, Tiêu cực 😟, Trung lập 😐).
        - **Độ tin cậy**: Điểm tự tin của model đối với kết quả dự đoán (0.0 đến 1.0).
        - **Từ khóa**: Cụm từ mang ý nghĩa chính sau khi lọc Stopwords.
        - **Batch Upload**: Có thể upload file (CSV/Excel) ở menu bên trái. Dữ liệu đọc từ cột đầu tiên.
        """)

    tabs = st.tabs(["💬 Phân tích & Chat", "📊 Dashboards", "⚖️ So sánh (A/B Testing)"])

    with tabs[0]:
        col_chat, col_hist = st.columns([2, 1])
        with col_chat:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
            
            if prompt := st.chat_input("Nhập phản hồi của bạn..."):
                lines = [l.strip() for l in prompt.splitlines() if l.strip()]
                for line in lines:
                    st.session_state.messages.append({"role": "user", "content": line})
                    with st.chat_message("user"):
                        st.markdown(line)
                    
                    res = cached_analyze(line)
                    st.session_state.history.append(res)
                    save_history(st.session_state.history)
                    
                    bot_reply = render_analysis(res)
                    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
                    with st.chat_message("assistant"):
                        st.markdown(bot_reply)
        
        with col_hist:
            st.subheader("Bản ghi dữ liệu")
            for i, item in enumerate(st.session_state.history):
                c_text, c_btn = st.columns([4, 1])
                c_text.caption(f"{item['text'][:40]}...")
                if c_btn.button("🗑️", key=f"del_{i}", help="Xóa phản hồi này"):
                    delete_feedback(i)

    with tabs[1]:
        if st.session_state.history:
            df = pd.DataFrame(st.session_state.history)
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.subheader("Phân bổ cảm xúc")
                st.bar_chart(df['sentiment'].value_counts())
            with col_chart2:
                st.subheader("Word Cloud")
                render_wordcloud(st.session_state.history)
                
            render_sentiment_timeline(st.session_state.history)
        else:
            st.info("Chưa có đủ dữ liệu để tạo biểu đồ.")

    with tabs[2]:
        # TODO 12: Chế độ so sánh
        st.subheader("Đánh giá A/B (Trước & Sau cải tiến)")
        colA, colB = st.columns(2)
        with colA:
            fileA = st.file_uploader("Upload Data Nhóm A (CSV)", type=["csv"], key="fileA")
        with colB:
            fileB = st.file_uploader("Upload Data Nhóm B (CSV)", type=["csv"], key="fileB")
            
        if fileA and fileB:
            dfA, dfB = pd.read_csv(fileA), pd.read_csv(fileB)
            resA = [cached_analyze(str(t))["sentiment"] for t in dfA.iloc[:, 0].dropna()]
            resB = [cached_analyze(str(t))["sentiment"] for t in dfB.iloc[:, 0].dropna()]
            
            chart_df = pd.DataFrame({
                "Nhóm": ["A (Trước)"] * len(resA) + ["B (Sau)"] * len(resB),
                "Cảm xúc": resA + resB
            })
            fig = px.histogram(chart_df, x="Nhóm", color="Cảm xúc", barmode="group")
            st.plotly_chart(fig, use_container_width=True)

    # ── Sidebar ──
    with st.sidebar:
        st.header("Workspace")
        # TODO 3: Hỗ trợ upload file CSV/Excel
        uploaded_file = st.file_uploader("Upload hàng loạt", type=["csv", "xlsx"])
        if uploaded_file and st.button("Xử lý File"):
            df_upload = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
            texts = df_upload.iloc[:, 0].dropna().tolist()
            
            for text in texts:
                res = cached_analyze(str(text))
                st.session_state.history.append(res)
                st.session_state.messages.append({"role": "user", "content": str(text)})
                st.session_state.messages.append({"role": "assistant", "content": render_analysis(res)})
                
            save_history(st.session_state.history)
            st.success(f"Đã xử lý {len(texts)} bản ghi mới!")
            st.rerun()

        # TODO 4: Export history
        st.divider()
        if st.session_state.history:
            df_history = pd.DataFrame(st.session_state.history)
            st.download_button(
                label="📥 Export Dữ liệu (CSV)",
                data=df_history.to_csv(index=False).encode('utf-8'),
                file_name="feedback_export.csv",
                mime="text/csv",
                use_container_width=True
            )

if __name__ == "__main__":
    main()