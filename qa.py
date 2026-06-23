import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# 1. 映射到你的 /chat/completions API
Settings.llm = Ollama(
    model="qwen2.5", 
    base_url="http://localhost:11434",
    request_timeout=60.0
)

# 2. 映射到你的 /embeddings API
# 注意：这里我们使用 "bge-m3" 作为专用的向量模型，它对中文的检索效果极好。
# 如果你本地还没这个模型，运行代码前请先在终端执行：ollama pull bge-m3
Settings.embed_model = OllamaEmbedding(
    model_name="bge-m3", 
    base_url="http://localhost:11434"
)

def main():
    data_dir = "./data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"📁 已自动为你创建 '{data_dir}' 文件夹，请把要读取的文件放进去后再运行我！")
        return

    if not os.listdir(data_dir):
        print(f"⚠️ '{data_dir}' 文件夹目前是空的，请放入至少一个文档（如txt/pdf）。")
        return

    print("📚 正在通过 /embeddings 接口为文档建立向量索引...")
    # 自动读取 data 文件夹中的文档
    documents = SimpleDirectoryReader(data_dir).load_data()
    
    # 这一步会隐式调用 /embeddings 接口，把文本转成密密麻麻的数字向量
    index = VectorStoreIndex.from_documents(documents)
    
    # 3. 创建带有长久记忆的聊天引擎
    # context 模式会在你提问时，自动检索最相关的文档切片，并连同对话历史一起传给 /chat/completions
    chat_engine = index.as_chat_engine(chat_mode="context", verbose=False)
    
    print("\n🚀 知识库构建成功！输入 'exit' 退出。")
    print("-" * 50)
    
    while True:
        user_input = input("\n👤 你的提问: ")
        if user_input.strip().lower() == 'exit':
            print("再见！")
            break
        if not user_input.strip():
            continue
            
        print("🤖 Qwen2.5 正在检索并思考...", end="\r")
        
        try:
            # 这一步会同时结合【历史上下文】+【/embeddings 检索到的内容】送给 /chat/completions
            response = chat_engine.chat(user_input)
            print(f"🤖 Qwen2.5: {response}")
        except Exception as e:
            print(f"\n❌ 出错了: {e}")

if __name__ == "__main__":
    main()