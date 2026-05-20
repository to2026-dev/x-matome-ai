import streamlit as st
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv
import os

st.set_page_config(
    page_title="XまとめAI",
    page_icon="🧠",
    layout="wide"
)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.title("XまとめAI")

st.caption("AIでX投稿を自動整理・要約")

if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.header("⚙️ 設定")

    mode = st.selectbox(
        "モード選択",
        ["ニュース風", "バズ風", "冷静解説風"]
    )

    st.caption("AIの出力スタイルを変更できます")

texts = st.text_area("X投稿を複数入力（改行OK）")

if st.button("🚀 要約する", use_container_width=True):

    if texts.strip() == "":
        st.warning("X投稿を入力してください")

    else:
        with st.spinner("AIがXを分析中..."):

            prompt = f"""
複数のX投稿をまとめてください。

条件：
・モード: {mode}
・3行以内
・箇条書き
・最後にハッシュタグを2個
・読みやすく
・共通テーマを整理

投稿：
{texts}
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            answer = response.choices[0].message.content

            title_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"""
次の内容に対して、
Xでバズりそうなタイトルを1個作ってください。

内容：
{answer}
"""
                    }
                ]
            )

            title = title_response.choices[0].message.content

            st.subheader("🔥 AIタイトル")
            st.write(title)

            st.subheader("📝 AIまとめ")

            st.markdown(
                f"""
                <div style="
                    background-color: #1e1e1e;
                    padding: 20px;
                    border-radius: 15px;
                    border: 1px solid #333;
                    margin-bottom: 20px;
                ">
                    {answer}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.code(answer)

            st.write(f"文字数: {len(answer)}")

            st.session_state.history.append({
                "mode": mode,
                "title": title,
                "summary": answer,
                "count": len(answer)
            })

            if len(answer) > 280:
                st.warning("280文字を超えています")
            else:
                st.success("280文字以内です")

st.divider()

st.subheader("📚 履歴")

if st.session_state.history:

    df = pd.DataFrame(st.session_state.history)

    csv = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "📥 CSVダウンロード",
        csv,
        "x_summary_history.csv",
        "text/csv"
    )

if st.button("履歴をクリア", key="clear_history"):
    st.session_state.history = []
    st.rerun()

for item in st.session_state.history:

    with st.container():

        st.markdown(f"### 🔥 {item['title']}")

        st.write(f"モード：{item['mode']}")

        st.markdown(
            f"""
            <div style="
                background-color: #1e1e1e;
                padding: 20px;
                border-radius: 15px;
                border: 1px solid #333;
                margin-bottom: 20px;
            ">
                {item["summary"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.caption(f"文字数：{item['count']}")

        st.divider()