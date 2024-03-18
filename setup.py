from cx_Freeze import setup, Executable
import sys

# アプリケーションのエントリーポイントを指定
main_script = 'main.py'

# cx_Freezeの設定
build_exe_options = {
    "packages": ["os", "sys", "pathlib", "logging", "PyQt5", "llama_index", "openai", "pdfminer"],  # 必要なパッケージやモジュール
    "include_files": [("input/", "input/")],  # コピーするフォルダやファイル。("ソースパス", "ターゲットパス")
}

# セットアップ設定
setup(
    name="文書検索チャットボット",
    version="0.1",
    description="Your Application Description",
    options={"build_exe": build_exe_options},
    executables=[Executable(main_script, base="Win32GUI" if sys.platform == "win32" else None)]
)