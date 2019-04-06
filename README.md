# DirectoryCleaner

■これは何？
指定したディレクトリ以下を再帰的にファイル検索し、重複したファイルを削除するツールです。

■注意事項
・重複したファイルが見つかった場合、最初に見つけたファイル以外を削除します。
・ファイル削除するかどうか、バックアップを取るなど気の利いたことはしませんので重要なファイルが存在する
　ディレクトリで実行しないでください。たとえばCドライブ指定して本ツールを使っても何の責任も持ちません。
・Windowsのファイル構造を前提に作られているのでWindows環境でしか正常に動作しません。

■動作環境
Python3.6以上
Windows7

■仕様例
python DirectoryCleaner.py -d C:\Users\Default
-dオプションでディレクトリを指定します。