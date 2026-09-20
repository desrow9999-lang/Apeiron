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

# ── 【極上のUI・オーロラダークCSS】 ──
st.markdown("""
    <style>
    /* 全体の背景とベースカラー */
    .stApp {
        background: radial-gradient(circle at top center, #0f172a 0%, #050508 100%);
        color: #f1f5f9;
    }
    
    /* ヘッダーデザイン */
    .app-header {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.7), rgba(15, 23, 42, 0.9));
        border: 1px solid rgba(129, 140, 248, 0.3);
        padding: 20px 24px;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
        margin-bottom: 24px;
        backdrop-filter: blur(10px);
    }
    
    .app-title {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 800;
        font-size: 1.6rem !important;
        background: linear-gradient(135deg, #c7d2fe, #e879f9, #38bdf8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 0 4px 0;
    }
    
    .app-subtitle {
        color: #94a3b8;
        font-size: 13px;
        margin: 0;
        letter-spacing: 0.5px;
    }
    
    /* チャット吹き出し（ユーザー） */
    div.stChatMessage[data-testid="stChatMessage-user"] {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    /* チャット吹き出し（ソクラテス） */
    div.stChatMessage[data-testid="stChatMessage-assistant"], div.stChatMessage[data-testid="stChatMessage-model"] {
        background: linear-gradient(135deg, rgba(49, 46, 129, 0.3), rgba(15, 23, 42, 0.9)) !important;
        border: 1px solid rgba(168, 85, 247, 0.3) !important;
        border-radius: 16px;
        padding: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    }
    
    div.stChatMessage p, div.stChatMessage span {
        color: #f8fafc !important;
        font-size: 15px !important;
        line-height: 1.7;
    }

    /* 入力中の文字を完璧にくっきり白文字にする設定 */
    input, textarea, div[data-baseweb="input"] input, div[data-baseweb="base-input"] textarea, .stChatInput textarea {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 15px !important;
    }
    
    .stChatInput textarea::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        opacity: 1 !important;
    }
    
    /* インフォメーション・分析カード */
    .insight-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.9), rgba(30, 27, 75, 0.5));
        border: 1px solid rgba(129, 140, 248, 0.25);
        padding: 16px;
        border-radius: 14px;
        margin-bottom: 20px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.4);
    }
    </style>
""", unsafe_allow_html=True)

# ── 【ヘッダー表示】 ──
st.markdown("""
    <div class="app-header">
        <div class="app-title">🌌 Apeiron <span style="font-size: 1.1rem; font-weight: 400; color: #c084fc;">（アペイロン）</span></div>
        <p class="app-subtitle">終わりなき問いを通じて、思考の深淵へとダイブするソクラテス的対話システム</p>
    </div>
""", unsafe_allow_html=True)

# ── 【APIキー管理】 ──
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

api_key_input = st.sidebar.text_input("⚙️ Gemini API Key", type="password", value=st.session_state.api_key)
if api_key_input:
    st.session_state.api_key = api_key_input.strip()

if not st.session_state.api_key:
    st.markdown("""
        <div class="insight-card">
            <h4 style="color: #a5b4fc; margin-top: 0; font-size: 16px;">🔑 APIキーの入力が必要です</h4>
            <p style="color: #cbd5e1; font-size: 13px; margin-bottom: 0;">
                思考の深淵を開くため、有効な<b>Gemini APIキー</b>をサイドバーまたは下記に入力してください。
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    user_key = st.text_input("ここにAPIキーを入力", type="password")
    if user_key:
        st.session_state.api_key = user_key.strip()
        st.rerun()
    st.stop()

# ── 【AI設定 (プロ仕様の厳格なシステムプロンプト)】 ──
genai.configure(api_key=st.session_state.api_key)

system_instruction = (
    "あなたは古代ギリシャの哲学者ソクラテスであり、現代の最高峰の知性を備えた壁打ちAI『Apeiron』です。"
    "ユーザーが持ち込む悩み、ビジネスの課題、抽象的なテーマに対し、決して直接的な解決策や答え、アドバイスを与えてはなりません。"
    "代わりに、ユーザーが自らの内なる前提、思い込み、矛盾に気づき、本質へと到達できるような『鋭く、美しく、本質を突く1つの問い』だけを投げ返してください。"
    "トーン＆マナーは、知的で洗練され、どこか神秘的で、ユーザーの思考を心地よく揺さぶるものにしてください。"
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=system_instruction
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["ようこそ、思索の旅へ。……今、あなたの頭の中にある『解きたい問い』や『ほどけない思考の糸』は何ですか？"]}
    ]

if "chat" not in st.session_state:
    history_for_gemini = [
        {"role": m["role"], "parts": m["parts"]} for m in st.session_state.messages
    ]
    st.session_state.chat = model.start_chat(history=history_for_gemini)

# ── 【サイドバー: 思考のコントロールルーム】 ──
with st.sidebar:
    st.header("🛠️ メタ・コントロール")
    if st.button("🔄 思索の旅をリセットする", use_container_width=True):
        st.session_state.messages = [
            {"role": "model", "parts": ["ようこそ、思索の旅へ。……今、あなたの頭の中にある『解きたい問い』や『ほどけない思考の糸』は何ですか？"]}
        ]
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()
        
    st.markdown("---")
    st.subheader("📊 思考のステータス")
    depth_count = len(st.session_state.messages) // 2
    st.metric(label="思考の深層階層", value=f"第 {depth_count} 階層")
    
    st.markdown("---")
    st.subheader("📥 記録と共有")
    
    if len(st.session_state.messages) > 1:
        log_text = "=== Apeiron 思考の記録 ===\n"
        for m in st.session_state.messages:
            role = "あなた" if m["role"] == "user" else "ソクラテス"
            log_text += f"[{role}]\n{m['parts'][0]}\n\n"
        
        st.download_button(
            label="📥 思考ログを保存",
            data=log_text,
            file_name=f"apeiron_insight_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )
        
        share_title = "🌌 無限ソクラテス対話『Apeiron』で思考の深淵を探索中。\n"
        share_hashtag = "#Apeiron #思考の壁打ち #哲学"
        tweet_text = urllib.parse.quote(f"{share_title}\n{share_hashtag}")
        twitter_url = f"https://twitter.com/intent/tweet?text={tweet_text}"
        
        st.markdown(
            f'<a href="{twitter_url}" target="_blank" style="text-decoration: none;"><div style="background: linear-gradient(135deg, #0ea5e9, #2563eb); color: white; padding: 10px 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 13px; margin-top: 10px; box-shadow: 0 4px 12px rgba(14,165,233,0.3);">🐦 Xでシェアする</div></a>',
            unsafe_allow_html=True
        )
    else:
        st.caption("対話が進むと保存・シェア機能が有効になります。")

# ── 【メインチャット画面の描画】 ──
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# ── 【ユーザー入力プロンプト】 ──
if prompt := st.chat_input("思考の断片や、問いに対する答えを入力..."):
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("model"):
        with st.spinner("思考の深層を漂っています..."):
            try:
                response = st.session_state.chat.send_message(prompt)
                ai_response = response.text
            except Exception as e:
                ai_response = f"思索の回廊で接続が揺らぎました。APIキーを確認してもう一度送信してください。（エラー: {e}）"
            st.markdown(ai_response)
            
    st.session_state.messages.append({"role": "model", "parts": [ai_response]})
    st.rerun()
