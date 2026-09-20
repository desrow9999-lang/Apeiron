import streamlit as st
import google.generativeai as genai
import datetime
import urllib.parse

# ページ設定
st.set_page_config(
    page_title="Apeiron - 無限ソクラテス", 
    page_icon="🌌", 
    layout="centered"
)

# ── 【入力文字くっきり・完全保証CSS】 ──
st.markdown("""
    <style>
    /* 全体の背景 */
    .stApp {
        background-color: #05070b;
        color: #f1f5f9;
    }
    
    /* 洗練されたタイトルコンテナ */
    .app-header {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(129, 140, 248, 0.2);
        padding: 16px 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }
    
    .app-title {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 800;
        font-size: 1.4rem !important;
        background: linear-gradient(135deg, #a5b4fc, #e879f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .app-subtitle {
        color: #94a3b8;
        font-size: 12px;
        margin: 0;
    }
    
    /* チャット吹き出し */
    div.stChatMessage {
        background-color: #0f172a !important;
        border: 1px solid rgba(129, 140, 248, 0.15) !important;
        border-radius: 14px;
        padding: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    div.stChatMessage p, div.stChatMessage span {
        color: #f8fafc !important;
        font-size: 14.5px !important;
        line-height: 1.6;
    }

    /* ── 【入力中の文字をハッキリくっきりさせる最強設定】 ── */
    input, textarea, div[data-baseweb="input"] input, div[data-baseweb="base-input"] textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    /* チャット入力エリア全体のテキスト・プレースホルダー対策 */
    .stChatInput textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-size: 15px !important;
    }
    .stChatInput textarea::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        opacity: 1 !important;
    }
    
    /* APIカード */
    .api-card {
        background: linear-gradient(145deg, #0f172a, #1e1b4b);
        border: 1px solid rgba(129, 140, 248, 0.4);
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ── 【スマート・ヘッダー】 ──
st.markdown("""
    <div class="app-header">
        <div class="app-title">🌌 Apeiron <span style="font-size: 1rem; font-weight: 400; color: #c084fc;">（アペイロン）</span></div>
        <p class="app-subtitle">終わりなき問いを通じて、思考の深淵へダイブするAI壁打ち</p>
    </div>
""", unsafe_allow_html=True)

# ── 【APIキー管理】 ──
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.sidebar.text_input("⚙️ Gemini API Key", type="password", value=st.session_state.api_key)
if api_key_input:
    st.session_state.api_key = api_key_input

if not st.session_state.api_key:
    st.markdown("""
        <div class="api-card">
            <h4 style="color: #a5b4fc; margin-top: 0; font-size: 16px;">🔑 APIキーの設定が必要です</h4>
            <p style="color: #cbd5e1; font-size: 13px; margin-bottom: 0;">
                アプリを動かすために、<b>Gemini APIキー</b>を入力してください。<br>（左側のメニューからも入力できます）
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    user_key = st.text_input("ここにAPIキーを入力", type="password")
    if user_key:
        st.session_state.api_key = user_key
        st.rerun()
    st.stop()

# ── 【AI設定】 ──
genai.configure(api_key=st.session_state.api_key)

system_instruction = (
    "あなたは古代の賢者であり、現代の最高峰の壁打ち相手であるソクラテス的問答法のAIです。"
    "ユーザーが持ち込んだ悩みやテーマに対し、決して直接的な解決策や答えを出してはいけません。"
    "ユーザーが自身の前提を疑い、本質に気づけるような『鋭く、しかし温かい1つの問い』だけを投げ返してください。"
    "対話はどこまでも深く、無限に続きます。トーンは知的で洗練され、どこか神秘的であってください。"
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["ようこそ、思索の旅へ。……今、あなたの頭の中にある『モヤモヤ』や『解きたい問い』は何ですか？"]}
    ]

# チャットセッションの初期化（エラー防止対応）
if "chat" not in st.session_state:
    history_for_gemini = [
        {"role": m["role"], "parts": m["parts"]} for m in st.session_state.messages
    ]
    st.session_state.chat = model.start_chat(history=history_for_gemini)

# ── 【サイドバーツールーム】 ──
with st.sidebar:
    st.header("🛠️ 思考のコントロール")
    if st.button("🔄 対話を最初からやり直す"):
        st.session_state.messages = [
            {"role": "model", "parts": ["ようこそ、思索の旅へ。……今、あなたの頭の中にある『モヤモヤ』や『解きたい問い』は何ですか？"]}
        ]
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()
        
    st.markdown("---")
    st.subheader("📥 ログ保存 & シェア")
    
    if len(st.session_state.messages) > 1:
        log_text = "--- Apeiron 思考の記録 ---\n"
        for m in st.session_state.messages:
            role = "あなた" if m["role"] == "user" else "ソクラテス"
            log_text += f"[{role}]\n{m['parts'][0]}\n\n"
        
        st.download_button(
            label="📥 思考ログをファイル保存",
            data=log_text,
            file_name=f"apeiron_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )
        
        share_title = "🌌 無限ソクラテス対話アプリ『Apeiron』で思考の深淵を覗いています。\n"
        share_hashtag = "#Apeiron #思考の壁打ち"
        tweet_text = urllib.parse.quote(f"{share_title}\n{share_hashtag}")
        twitter_url = f"https://twitter.com/intent/tweet?text={tweet_text}"
        
        st.markdown(
            f'<a href="{twitter_url}" target="_blank" style="text-decoration: none;"><div style="background: linear-gradient(135deg, #0ea5e9, #2563eb); color: white; padding: 10px 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 13px; margin-top: 10px; box-shadow: 0 4px 12px rgba(14,165,233,0.3);">🐦 Xで思考をシェアする</div></a>',
            unsafe_allow_html=True
        )
    else:
        st.info("対話が進むと保存・シェア機能が有効になります。")

# ── 【思考の深さカウンター】 ──
depth_count = len(st.session_state.messages) // 2
st.markdown(f"<p style='text-align: right; color: #818cf8; font-size: 12px; margin-bottom: 10px;'>🧠 対話の深さ: 第 {depth_count} 階層</p>", unsafe_allow_html=True)

# ── 【チャット履歴の表示】 ──
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# ── 【ユーザー入力】 ──
if prompt := st.chat_input("あなたの考えや答えを入力..."):
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("model"):
        with st.spinner("思考の深淵を覗いています..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                ai_response = response.text
            except Exception as e:
                ai_response = f"思索の途中で波乱が起きました。もう一度送信してください。（エラー詳細: {e}）"
            st.markdown(ai_response)
            
    st.session_state.messages.append({"role": "model", "parts": [ai_response]})
    st.rerun()
