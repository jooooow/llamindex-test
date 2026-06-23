import os
import streamlit as st
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# ================= 1. モデル設定の初期化 =================
@st.cache_resource  # ページ更新時の重複接続を避けるためキャッシュを使用
def init_models():
    Settings.llm = Ollama(
        model="qwen2.5", 
        base_url="http://localhost:11434",
        request_timeout=60.0
    )
    Settings.embed_model = OllamaEmbedding(
        model_name="bge-m3", 
        base_url="http://localhost:11434"
    )

init_models()

# ================= 2. 知識ベースとエンジンの初期化 =================
@st.cache_resource(show_spinner=False)
def init_chat_engine():
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        return None, f"📁 '{data_dir}' フォルダを作成しました。ファイルを配置した後にページを再読み込みしてください。"
        
    if not os.listdir(data_dir):
        return None, f"⚠️ '{data_dir}' フォルダが空です。ドキュメント（txt/pdf/md）を配置した後にページを再読み込みしてください。"
        
    try:
        # ドキュメントを自動読み込みしてインデックスを構築
        documents = SimpleDirectoryReader(data_dir).load_data()
        index = VectorStoreIndex.from_documents(documents)
        # 文脈を維持するチャットエンジンを作成
        chat_engine = index.as_chat_engine(chat_mode="context", verbose=False)
        return chat_engine, "✅ 知識ベースの読み込みに成功しました！"
    except Exception as e:
        return None, f"❌ 読み込み失敗: {str(e)}"

# ================= 3. Streamlit ページレイアウト =================
st.set_page_config(page_title="ローカル知識ベースQA (Qwen2.5)", page_icon="🤖", layout="centered")
st.title("🤖 Qwen2.5 ローカルドキュメント知識ベース")
st.caption("Powered by LlamaIndex + Ollama + Streamlit")

# サイドバーの状態表示
with st.sidebar:
    st.header("知識ベースの状態")
    chat_engine, status_msg = init_chat_engine()
    st.info(status_msg)
    st.write("現在の読み込みパス: `./data`")
    if st.button("🔄 ファイルを再読み込み"):
        st.cache_resource.clear()
        st.rerun()

# 履歴管理のためのセッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは！data フォルダ内のすべてのドキュメントを読み込みました。何かお手伝いできることはありますか？"}
    ]
if "chat_engine_instance" not in st.session_state and chat_engine is not None:
    st.session_state.chat_engine_instance = chat_engine

# チャット履歴のレンダリング
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================= 4. ユーザー入力の処理 =================
if prompt := st.chat_input("ドキュメントについて質問する..."):
    # エンジンが初期化されていない場合は処理を中断
    if "chat_engine_instance" not in st.session_state:
        st.error("エラー: まずローカルに `./data` フォルダを作成し、ドキュメントを配置してください。")
        st.stop()

    # 1. ユーザーの入力を画面に表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. AIの応答生成とローディング表示
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # LlamaIndex から応答を取得
                response = st.session_state.chat_engine_instance.chat(prompt)
                answer = response.response
                
                # 結果を画面に出力
                st.write(answer)
                # 履歴に追加
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")