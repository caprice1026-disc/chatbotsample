import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit, QLineEdit
from PyQt5.QtCore import Qt
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
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.llms.openai import OpenAI
from pdfminer.high_level import extract_text
from pathlib import Path
import os
import shutil
from pathlib import Path
# モデル変更
Settings.llm = OpenAI(model="gpt-4-turbo-preview", temperature=0)

openai.api_key = os.environ["OPENAI_API_KEY"]


class LogHandler(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('文書検索チャットボット')
        self.setGeometry(100, 100, 800, 600)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)

        self.chat_input = QLineEdit()
        self.chat_input.setEnabled(False)  # 初期状態では無効
        self.chat_input.returnPressed.connect(self.send_chat)  # エンターキーで送信

        self.send_button = QPushButton('送信')
        self.send_button.clicked.connect(self.send_chat)
        self.send_button.setEnabled(False)  # 初期状態では無効


        layout = QVBoxLayout()
        layout.addWidget(self.log_text)
        layout.addWidget(self.chat_input)
        layout.addWidget(self.send_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # ロギング設定
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        log_handler = LogHandler(self.log_text)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(log_handler)

        self.index = None
        self.initialize_index() 


    def initialize_index(self):
        logging.info("インデックス作成を開始します。")
        QApplication.processEvents()  # UIの更新を確実にする

        if getattr(sys, 'frozen', False):
        # exeとして実行されている場合、_MEIPASSを基準にinputフォルダのパスを設定
            application_path = Path(getattr(sys, '_MEIPASS', Path(__file__).parent))
        else:
        # スクリプトとして実行されている場合、現在のファイルのディレクトリを基準に設定
            application_path = Path(__file__).parent

        input_dir = application_path / "input"
        output_dir = "./処理後データ"
        os.makedirs(output_dir, exist_ok=True)  # 出力ディレクトリがなければ作成

        # inputディレクトリ内のPDFファイルを処理
    # inputディレクトリ内のファイルを処理
        for file_path in Path(input_dir).glob("*"):
            if file_path.suffix.lower() == ".pdf":
                # PDFファイルの場合、テキストを抽出して保存
                logging.info(f"PDFファイル {file_path} のテキスト抽出を開始します。")
                text = extract_text(file_path)
                output_file_path = Path(output_dir) / (file_path.stem + ".txt")
                with open(output_file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                logging.info(f"PDFファイル {file_path} のテキスト抽出が完了し、{output_file_path} に保存されました。")
            else:
            # PDF以外のファイルはそのまま移動
                destination_path = Path(output_dir) / file_path.name
                logging.info(f"PDF以外のファイル {file_path} を {destination_path} に移動します。")
                shutil.copy(str(file_path), str(destination_path))
                logging.info(f"ファイル {file_path} の移動が完了しました。")

        # 処理後のテキストファイルからインデックスを作成
        documents = SimpleDirectoryReader(output_dir).load_data()
        self.index = VectorStoreIndex.from_documents(documents)
        self.index.storage_context.persist(persist_dir="./index")
        logging.info("インデックスの保存が完了しました。")
        # インデックスを保存
        self.index.storage_context.persist(persist_dir="./index")
        logging.info("インデックスの保存が完了しました。")
            # クエリエンジン作成
        self.query_engine = self.index.as_query_engine()
        logging.info("クエリエンジンの作成が完了しました。")
        self.chat_input.setEnabled(True)
        self.send_button.setEnabled(True)
        logging.info("クエリエンジンの作成が完了しました。")
        
    def send_chat(self):
        question = self.chat_input.text()
        logging.info(f"送信された質問: {question}")  # デバッグ情報を追加
        if not question:
            logging.error("質問が空です。")
            return
        if not self.query_engine:
            logging.error("クエリエンジンが初期化されていません。")
            return
        try:
            response = self.query_engine.query(question)
            logging.info(f"回答: {response}")
        except Exception as e:
            logging.error(f"クエリの処理中にエラーが発生しました: {e}")
        self.chat_input.clear()

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