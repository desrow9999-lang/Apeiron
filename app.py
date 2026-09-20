import streamlit as st
import google.generativeai as genai
import datetime

# ページ設定（ダークテーマと洗練されたアイコン）
st.set_page_config(
    page_title="Apeiron - 無限ソクラテス", 
    page_icon="🌌", 
    layout="centered"
)

# ── 【スタイリッシュ化のためのCSSデザイン調整】 ──
st.markdown("""
    <style>
    /* 全体の背景とフォントの洗練 */
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
    }
    /* タイトルのスタイリング */
    h1 {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    /* チャットコンテナの微調整 */
    .stChatMessage {
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
""", unsafe_allow_html=True)

# ── 【UIヘッダー】 ──
st.title("🌌 Apeiron（アペイロン）")
st.caption("終わりなき問いを通じて、思考の深淵へダイブするAI壁打ちアプリ。")

# サイドバー：APIキーと追加機能
with st.sidebar:
    st.header("⚙️ 設定 & ツール")
    api_key = st.text_input("Gemini API Key", type="password")
    
    st.markdown("---")
    st.subheader("💡 思考の保存")
    
    # ── 【機能追加①：対話ログのエクスポート（ダウンロード）機能】 ──
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        # 履歴をテキスト形式に変換
        log_text = "--- Apeiron 思考の記録 ---\n"
        for m in st.session_state.messages:
            role = "あなた" if m["role"] == "user" else "ソクラテス"
            log_text += f"[{role}]\n{m['parts'][0]}\n\n"
        
        st.download_button(
            label="📥 思考ログをダウンロード",
            data=log_text,
            file_name=f"apeiron_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            help="これまでの問答の記録をスマホやPCに保存します。"
        )
    else:
        st.info("対話が進むとログのダウンロードが可能になります。")

if not api_key:
    st.warning("👈 左側のサイドバーからGemini APIキーを入力してください。")
else:
    genai.configure(api_key=api_key)
    
    # モデルの初期化（プロンプトの強化）
    system_instruction = (
        "あなたは古代の賢者であり、現代の最高峰の壁打ち相手であるソクラテス的問答法のAIです。"
        "ユーザーが持ち込んだ悩みやテーマに対し、決して直接的な解決策や答えを出してはいけません。"
        "ユーザーが自身の前提を疑い、本質に気づけるような『鋭く、しかし温かい1つの問い』だけを投げ返してください。"
        "対話はどこまでも深く、無限に続きます。トーンは知的で洗練され、どこか神秘的であってください。"
    )
    
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        system_instruction=system_instruction
    )
    
    # チャット履歴の初期化
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "model", "parts": ["ようこそ、思索の旅へ。……今、あなたの頭の中にある『モヤモヤ』や『解きたい問い』は何ですか？"]}
        ]
        st.session_state.chat = model.start_chat(history=[])

    # ── 【機能追加②：思考の核心・キーワードのリアルタイム分析表示】 ──
    if len(st.session_state.messages) > 3:
        with st.expander("🔮 現在の思考の核心（AIアナリティクス）", expanded=False):
            with st.spinner("思考の軸を抽出中..."):
                try:
                    summary_prompt = "これまでの対話の核心を、鋭い1つのキーワードまたは短い哲学的な命題として抽出してください。解説は不要です。"
                    summary_res = st.session_state.chat.send_message(summary_prompt)
                    st.markdown(f"**現在のテーマ軸:** `{summary_res.text}`")
                except:
                    st.write("対話が深まるにつれてここにテーマの核心が表示されます。")

    # 履歴の表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["parts"][0])

    # ユーザーからの入力
    if prompt := st.chat_input("あなたの考えや答えを入力..."):
        st.session_state.messages.append({"role": "user", "parts": [prompt]})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AIからの応答生成
        with st.chat_message("model"):
            with st.spinner("思考の深淵を覗いています..."):
                response = st.session_state.chat.send_message(prompt)
                ai_response = response.text
                st.markdown(ai_response)
                
        st.session_state.messages.append({"role": "model", "parts": [ai_response]})
        st.rerun()
