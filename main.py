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
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QLineEdit, QTextEdit, QLabel
from PyQt5.QtCore import Qt
from configparser import ConfigParser

# ロギングの設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('文書検索アプリケーション')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()
        self.label = QLabel('ファイルを選択してください:')
        layout.addWidget(self.label)
        self.button = QPushButton('ファイル選択')
        self.button.clicked.connect(self.openFileNameDialog)
        layout.addWidget(self.button)

        self.query_label = QLabel('質問:')
        layout.addWidget(self.query_label)
        self.query_input = QLineEdit()
        layout.addWidget(self.query_input)

        self.search_button = QPushButton('検索')
        self.search_button.clicked.connect(self.search_documents)
        layout.addWidget(self.search_button)

        self.result_text = QTextEdit()
        layout.addWidget(self.result_text)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.PERSIST_DIR = ".bis"
        self.index = None
        self.load_api_key_and_initialize_index()

    def load_api_key_and_initialize_index(self):
        config = ConfigParser()
        config.read('config.ini')
        openai.api_key = config['DEFAULT']['OPENAI_API_KEY']
        # インデックスの初期化または読み込みをここに実装
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
        self.index = index
        

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            self.label.setText(f'選択されたファイル: {fileName}')
            # 選択されたファイルを使ってインデックスを作成または更新

    def search_documents(self):
        question = self.query_input.text()
        # インデックスを使って質問に答え、結果をself.result_textに表示

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


'''# ロギングの設定
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
'''