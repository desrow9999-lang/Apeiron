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

# ── 【究極のスタイリッシュ・ダークテーマCSS】 ──
st.markdown("""
    <style>
    .stApp {
        background-color: #030712;
        color: #f3f4f6;
    }
    h1 {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-weight: 800;
        background: linear-gradient(135deg, #a5b4fc, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    /* チャットメッセージの洗練 */
    .stChatMessage {
        background-color: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 12px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    /* カードデザイン */
    .api-card {
        background: linear-gradient(145deg, #111827, #1f2937);
        border: 1px solid rgba(129, 140, 248, 0.3);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ── 【ヘッダー】 ──
st.title("🌌 Apeiron（アペイロン）")
st.caption("✨ 終わりなき問いを通じて、思考の深淵へダイブするAI壁打ちアプリ。")
st.markdown("---")

# ── 【APIキーの管理（メイン画面にわかりやすく配置）】 ──
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# サイドバーまたはメインでのAPIキー入力
api_key_input = st.sidebar.text_input("⚙️ Gemini API Key", type="password", value=st.session_state.api_key)
if api_key_input:
    st.session_state.api_key = api_key_input

# APIキーが未入力の場合は、メイン画面に美しいカードを表示して迷わせない
if not st.session_state.api_key:
    st.markdown("""
        <div class="api-card">
            <h3 style="color: #a5b4fc; margin-top: 0;">🔑 はじめに：APIキーの設定が必要です</h3>
            <p style="color: #9ca3af; font-size: 14px;">
                このアプリを動かすには、Google AI Studio等で取得した <b>Gemini APIキー</b> が必要です。<br>
                下の入力欄、または左側のメニュー（サイドバー）に入力してください。
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    user_key = st.text_input("ここにGemini APIキーを入力", type="password")
    if user_key:
        st.session_state.api_key = user_key
        st.rerun()
        
    st.stop() # キーが入るまでここで処理をストップ

# ── 【API設定完了後のメイン処理】 ──
genai.configure(api_key=st.session_state.api_key)

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

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "model", "parts": ["ようこそ、思索の旅へ。……今、あなたの頭の中にある『モヤモヤ』や『解きたい問い』は何ですか？"]}
    ]
    st.session_state.chat = model.start_chat(history=[])

# ── 【サイドバー：ツール＆シェア機能】 ──
with st.sidebar:
    st.header("🛠️ ツールーム")
    if st.button("🔄 対話をリセットする"):
        st.session_state.messages = [
            {"role": "model", "parts": ["ようこそ、思索の旅へ。……今、あなたの頭の中にある『モヤモヤ』や『解きたい問い』は何ですか？"]}
        ]
        st.session_state.chat = model.start_chat(history=[])
        st.rerun()
        
    st.markdown("---")
    st.subheader("📥 保存・シェア")
    
    if len(st.session_state.messages) > 1:
        log_text = "--- Apeiron 思考の記録 ---\n"
        for m in st.session_state.messages:
            role = "あなた" if m["role"] == "user" else "ソクラテス"
            log_text += f"[{role}]\n{m['parts'][0]}\n\n"
        
        st.download_button(
            label="📥 思考ログを保存",
            data=log_text,
            file_name=f"apeiron_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
        )
        
        share_title = "🌌 無限ソクラテス対話アプリ『Apeiron』で思考の深淵を覗いています。\n"
        share_hashtag = "#Apeiron #思考の壁打ち"
        tweet_text = urllib.parse.quote(f"{share_title}\n{share_hashtag}")
        twitter_url = f"https://twitter.com/intent/tweet?text={tweet_text}"
        
        st.markdown(
            f'<a href="{twitter_url}" target="_blank" style="text-decoration: none;"><div style="background: linear-gradient(135deg, #0ea5e9, #2563eb); color: white; padding: 10px 15px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 14px; margin-top: 10px; box-shadow: 0 4px 12px rgba(14,165,233,0.3);">🐦 Xで思考をシェアする</div></a>',
            unsafe_allow_html=True
        )
    else:
        st.info("対話が進むと保存・シェア機能が有効になります。")

# ── 【思考の核心アナリティクス】 ──
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
