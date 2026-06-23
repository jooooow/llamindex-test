import os
import streamlit as st
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# ================= 0. 极致纯净·页面配置与 CSS =================
st.set_page_config(
    page_title="DocuMind | 本地知识库", 
    page_icon="📄", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# 注入现代极简白 CSS，彻底告别怪异色彩
st.markdown("""
<style>
    /* 强行覆盖全局背景为极其干净的暖白/浅灰 */
    .stApp {
        background-color: #fafafa !important;
    }
    
    /* 标题：克制、洗练的炭黑色，无任何渐变 */
    .main-title {
        color: #1a1a1a;
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -0.8px;
        margin-bottom: 5px;
    }
    
    /* 侧边栏：纯白底色加极细微的阴影，营造悬浮感 */
    .status-card {
        padding: 16px;
        border-radius: 10px;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    
    /* 优化侧边栏整体背景与主色调一致 */
    section[data-testid="stSidebar"] {
        background-color: #f4f4f5 !important;
        border-right: 1px solid #e4e4e7;
    }
    
    /* 克制微调 Streamlit 自带的聊天输入框边缘 */
    .stChatInputContainer {
        border-radius: 8px !important;
        border: 1px solid #e4e4e7 !important;
        background-color: #ffffff !important;
    }
    
    /* 强行改变部分文案和代码块的配色，使其在白底下清晰 */
    code {
        color: #2563eb !important; /* 优雅的克莱因蓝 */
        background-color: #f1f5f9 !important;
    }
</style>
""", unsafe_allow_html=True)


# ================= 1. モデル設定の初期化 =================
@st.cache_resource
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
        return None, "📁 `data/` フォルダを作成しました。ファイルを配置して再読み込みしてください。", "info"
        
    if not os.listdir(data_dir):
        return None, "⚠️ `data/` フォルダが空です。ドキュメントを配置してください。", "warning"
        
    try:
        documents = SimpleDirectoryReader(data_dir).load_data()
        index = VectorStoreIndex.from_documents(documents)
        chat_engine = index.as_chat_engine(chat_mode="context", streaming=True, verbose=False)
        return chat_engine, f"📄 知識ベースの同期が完了しました ({len(documents)} 件の文書)", "success"
    except Exception as e:
        return None, f"❌ 読み込み失敗: {str(e)}", "error"


# ================= 3. サイドバー（システム管理） =================
with st.sidebar:
    st.markdown("<h2 style='color: #09090b; font-size: 1.1rem; font-weight: 600; letter-spacing: -0.3px;'>CONSOLE</h2>", unsafe_allow_html=True)
    st.write("---")
    
    chat_engine, status_msg, status_type = init_chat_engine()
    
    # 状态提示（利用 Streamlit 自带的原生组件，在白底下非常干净）
    if status_type == "success":
        st.success(status_msg)
    elif status_type == "warning":
        st.warning(status_msg)
    elif status_type == "error":
        st.error(status_msg)
    else:
        st.info(status_msg)
        
    # 纯白卡片，灰字蓝标
    st.markdown(f"""
    <div class="status-card">
        <span style="color: #71717a; font-size: 0.8rem; font-weight: 500; display:block; margin-bottom:4px;">ENVIRONMENT</span>
        <code>LlamaIndex + Ollama</code>
        <div style="margin-top: 14px;"></div>
        <span style="color: #71717a; font-size: 0.8rem; font-weight: 500; display:block; margin-bottom:4px;">ACTIVE MODELS</span>
        <span style="color: #18181b; font-size: 0.9rem; display:block;">LLM: <b>Qwen2.5</b></span>
        <span style="color: #18181b; font-size: 0.9rem; display:block;">EMB: <b>bge-m3</b></span>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🔄 インデックスを再構築", use_container_width=True):
        st.cache_resource.clear()
        st.rerun()


# ================= 4. メイン画面レイアウト =================
# 炭黑纯净大标题
st.markdown('<p class="main-title">DocuMind AI</p>', unsafe_allow_html=True)
st.markdown("<p style='color: #71717a; font-size: 0.95rem; margin-top: -5px;'>ローカルドキュメントのための高精度ナレッジエンジン</p>", unsafe_allow_html=True)
st.write("---")

# 履歴管理のためのセッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "こんにちは。読み込まれたドキュメントについて解析や質問への回答を行うことができます。"}
    ]
if "chat_engine_instance" not in st.session_state and chat_engine is not None:
    st.session_state.messages.append({"role": "assistant", "content": "💡 **ナレッジベースが利用可能になりました。** いつでも質問をどうぞ。"})
    st.session_state.chat_engine_instance = chat_engine

# チャット履歴のレンダリング
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ================= 5. ユーザー入力の処理（流式タイピング） =================
if prompt := st.chat_input("ドキュメントについて質問する..."):
    if "chat_engine_instance" not in st.session_state:
        st.error("エラー: ナレッジベースが利用できません。`./data` にファイルを配置してください。")
        st.stop()

    # 1. ユーザーの入力を画面に表示
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. AIの応答生成（流式アニメーション）
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            streaming_response = st.session_state.chat_engine_instance.stream_chat(prompt)
            # 流式打字机输出
            full_response = response_placeholder.write_stream(streaming_response.response_gen)
            
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"応答生成中にエラーが発生しました: {e}")