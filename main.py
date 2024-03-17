import openai
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
    Settings
)
import logging
import sys
import openai
from llama_index.llms.openai import OpenAI
from pathlib import Path
import os

# ロギングの設定
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler(sys.stdout))

# モデル変更
Settings.llm = OpenAI(model="gpt-4-turbo-preview", temperature=0)

openai.api_key = os.environ["OPENAI_API_KEY"]

PERSIST_DIR = ".bis"
# ストレージが既に存在するかチェック
if not os.path.exists(PERSIST_DIR):
    logger.info("ストレージディレクトリが存在しません。インデックスを生成します。")
    # この部分をUIからのファイル選択に置き換える
    documents = SimpleDirectoryReader("./input").load_data()
    index = VectorStoreIndex.from_documents(documents)
    # ストレージに保存
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    logger.info("既存のストレージディレクトリからインデックスをロードします。")
    # 既存のインデックスをロード
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
# クエリエンジンの作成
query_engine = index.as_query_engine()
# ここにUIからの質問を入れる
question = ""

response = query_engine.query(question)
# 出力先をUIに変更
print(response)