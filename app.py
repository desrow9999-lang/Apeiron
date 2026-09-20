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

# ── 【スマホ完全対応・入力文字くっきりスタイリッシュCSS】 ──
st.markdown("""
    <style>
    /* 全体の背景 */
    .stApp {
        background-color: #05070b;
        color: #f1f5f9;
    }
    
    /* スマホでも絶対に崩れない洗練されたタイトルコンテナ */
    .app-header {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6), rgba(15, 23, 42, 0.8));
        border: 1px solid rgba(129, 140, 248, 0.2);
        padding: 16px 20px;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
        display: flex;
        flex-direction: column;
        gap: 4px;
    }
    
    .app-title {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 800;
        font-size: 1.4rem !important;
        background: linear-gradient(135deg, #a5b4fc, #e879f9);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    .app-subtitle {
        color: #94a3b8;
        font-size: 12px;
        margin: 0;
    }
    
    /* チャット吹き出しの視認性改善 */
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

    /* ── 【入力中の文字＆プレースホルダーをハッキリ見やすくする設定】 ── */
    /* テキスト入力欄（APIキーや通常入力）の文字を白くくっきりさせる */
    .stTextInput input {
        color: #ffffff !important;
        background-color: #0b0f19 !important;
        border: 1px solid rgba(129, 140, 248, 0.3) !important;
    }
    
    /* チャット入力欄（st.chat_input）の文字とプレースホルダーの色を最適化 */
    .stChatInput textarea {
        color: #ffffff !important;
        font-size: 15px !important;
    }
    .stChatInput textarea::placeholder {
        color: #94a3b8 !important;
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
    st.session_state.chat = model.start_chat(history=[])

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

# ── 【思考の深さカウンター & 核心アナリティクス】 ──
depth_count = len(st.session_state.messages) // 2
st.markdown(f"<p style='text-align: right; color: #818cf8; font-size: 12px; margin-bottom: 10px;'>🧠 対話の深さ: 第 {depth_count} 階層</p>", unsafe_allow_html=True)

if len(st.session_state.messages) > 3:
    with st.expander("🔮 現在の思考の核心（AIアナリティクス）", expanded=False):
        with st.spinner("思考の軸を抽出中..."):
            try:
                summary_prompt = "これまでの対話の核心を、鋭い1つのキーワードまたは短い哲学的な命題として抽出してください。解説は不要です。"
                summary_res = st.session_state.chat.send_message(summary_prompt)
                st.markdown(f"**現在のテーマ軸:** `{summary_res.text}`")
            except:
                st.write("対話が深まるにつれてここにテーマの核心が表示されます。")

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
            response = st.session_state.chat.send_message(prompt)
            ai_response = response.text
            st.markdown(ai_response)
            
    st.session_state.messages.append({"role": "model", "parts": [ai_response]})
    st.rerun()
