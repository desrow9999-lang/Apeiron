import streamlit as st
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="Apeiron - 無限ソクラテス", page_icon="🌌", layout="centered")

st.title("🌌 Apeiron（アペイロン）")
st.caption("終わりなき問いを通じて、思考の深淵へダイブするAI壁打ちアプリ。")

# Gemini APIキーの設定（シークレットまたはサイドバー入力）
api_key = st.sidebar.text_input("Gemini API Key", type="password")

if not api_key:
    st.warning("左側のサイドバーからGemini APIキーを入力してください。")
else:
    genai.configure(api_key=api_key)
    
    # モデルの初期化（システムプロンプト設定）
    system_instruction = (
        "あなたはソクラテス的問答法を極めたAIです。"
        "ユーザーが入力した悩みやテーマに対し、決して直接的な解決策や答えを出してはいけません。"
        "ユーザーが自身の前提を疑い、本質に気づけるような『鋭く、しかし温かい1つの問い』だけを投げ返してください。"
        "対話はどこまでも深く、無限に続きます。"
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
                # チャットの継続
                response = st.session_state.chat.send_message(prompt)
                ai_response = response.text
                st.markdown(ai_response)
                
        st.session_state.messages.append({"role": "model", "parts": [ai_response]})
