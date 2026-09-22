import streamlit as st
from streamlit_autorefresh import st_autorefresh

def add_keep_alive(interval_minutes=10):
    """
    Streamlitアプリのスリープを防ぐための自動リロード機能を追加する関数
    :param interval_minutes: リロードする間隔（分）デフォルトは10分
    """
    # ミリ秒に変換
    interval_ms = interval_minutes * 60 * 1000
    
    # 自動リロードの実行
    count = st_autorefresh(interval=interval_ms, limit=None, key="global_keep_alive_refresh")
    
    # サイドバー等でこっそり動作確認できるようにする（不要ならコメントアウト可能）
    with st.sidebar:
        st.caption(f"🔄 Keep-Alive Active (Count: {count})")
