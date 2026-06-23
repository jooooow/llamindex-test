import os
import streamlit as nn
import streamlit as st
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# ================= 1. 初始化模型配置 =================
@st.cache_resource  # 使用缓存避免每次页面刷新都重复连接模型
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

# ================= 2. 初始化知识库与引擎 =================
@st.cache_resource(show_spinner=False)
def init_chat_engine():
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        return None, f"📁 已创建 '{data_dir}' 文件夹，请放入文件后刷新页面。"
        
    if not os.listdir(data_dir):
        return None, f"⚠️ '{data_dir}' 文件夹为空，请放入文档（txt/pdf/md）后刷新页面。"
        
    try:
        # 自动读取并构建索引
        documents = SimpleDirectoryReader(data_dir).load_data()
        index = VectorStoreIndex.from_documents(documents)
        # 创建带有上下文检索记忆的聊天引擎
        chat_engine = index.as_chat_engine(chat_mode="context", verbose=False)
        return chat_engine, "✅ 知识库加载成功！"
    except Exception as e:
        return None, f"❌ 加载失败: {str(e)}"

# ================= 3. Streamlit 页面布局 =================
st.set_page_config(page_title="本地知识库问答 (Qwen2.5)", page_icon="🤖", layout="centered")
st.title("🤖 Qwen2.5 本地文档知识库")
st.caption("基于 LlamaIndex + Ollama + Streamlit 驱动")

# 侧边栏状态显示
with st.sidebar:
    st.header("知识库状态")
    chat_engine, status_msg = init_chat_engine()
    st.info(status_msg)
    st.write("当前读取路径: `./data`")
    if st.button("🔄 重新读取文件"):
        st.cache_resource.clear()
        st.rerun()

# 初始化 Streamlit 的会话状态（用于维持 Web 端聊天记录）
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "你好！我已经阅读了 data 文件夹下的所有文档，有什么可以帮你的？"}
    ]
if "chat_engine_instance" not in st.session_state and chat_engine is not None:
    st.session_state.chat_engine_instance = chat_engine

# 渲染历史聊天记录
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================= 4. 处理用户输入 =================
if prompt := st.chat_input("向你的文档提问吧..."):
    # 如果引擎没初始化成功，不执行后续
    if "chat_engine_instance" not in st.session_state:
        st.error("请先在本地创建 ./data 文件夹并放入文档。")
        st.stop()

    # 1. 在界面上显示用户的输入
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # 2. 调用大模型并显示思考状态
    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            try:
                # 获取 LlamaIndex 的响应
                response = st.session_state.chat_engine_instance.chat(prompt)
                answer = response.response
                
                # 在页面输出结果
                st.write(answer)
                # 记录进历史对话列表
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"出错了: {e}")