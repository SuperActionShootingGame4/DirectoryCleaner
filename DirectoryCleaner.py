import glob
import os
import csv
import hashlib
import sqlite3
import shutil
import math
from datetime import datetime
from pathlib import Path
#from contextlib import closing
from argparse import ArgumentParser

FILE_SIZE = 0
DB_NAME = 'test.db'
CSV_NAME = "test.csv"

#MD5計算
def hash_md5(path):
	with open(path, "rb") as fileObject:
		binary = fileObject.read()
		md5 = hashlib.md5(binary).hexdigest()
	fileObject.closed
	return md5

#ファイルリスト作成
def listup_files(targetPath):
	print("Start listup_files()")
	scanPath = Path(targetPath)
	fileList = list(scanPath.glob("**/*"))
	#scanPath = targetPath + "/*"
	#fileList = glob.glob(scanPath)
	print("Complete listup_files()")
	return fileList

#CSVにlistの内容を追記する
def write_csv(path, list):
	with open(path, 'a', encoding="utf_8_sig", errors='ignore') as fileObject:
		writer = csv.writer(fileObject, lineterminator='\n')
		writer.writerow(list)
	fileObject.closed
	return True

#DBとCSVのフルパスを作成する
def make_path(targetPath):
	dateTime = datetime.now().strftime("%Y_%m%d_%H%M")
	dbPath = targetPath + os.sep + dateTime + ".db"
	csvPath = targetPath + os.sep + dateTime + ".csv"
	return dbPath, csvPath

#ファイルをコピーする
def copy_file(dbPath):
	if Path(dbPath).is_file():
		src = dbPath
		dest = dbPath + ".before"
		shutil.copyfile(src, dest)
	return True

#コンソールプログレスバーを表示する
def view_progressbar(current_num, length):
	progress = (current_num/length)*100
	barRange = math.floor(progress/10)
	barString = "=" * barRange
	if(barRange >= 10):
		print("\r"+ "[" + barString.ljust(10)+ "]" 
			+ " {0:.0f}%".format(progress)+" Complete")
	else:
		print("\r"+ "[" + barString.ljust(10)+ "]" 
			+ " {0:.0f}%".format(progress), end="")
	return

#ファイルリストのDBを作成 (ファイルのMD5ハッシュ取得)
def create_db(fileList, dbPath, csvPath):
	print("Start create_db()")
	if not fileList:
		return
	if Path(dbPath).is_file():
		os.remove(dbPath)
	# with closing()~としたらdbが閉じなかった…
	#with closing(sqlite3.connect(dbPath)) as connection :
	with sqlite3.connect(dbPath) as connection :
		cursor = connection.cursor()
		table = '''CREATE TABLE fileListTable ( id int, 
												file_name varchar(256), 
												file_path varchar(258), 
												file_ext varchar(256), 
												file_size int,
												file_time int, 
												file_uid int,
												file_md5 int )'''
		cursor.execute(table)
		write_csv(csvPath, ["id", "file_name", "file_path", "file_ext", 
							"file_size", "file_time", "file_uid", "file_md5"])
		write_csv(csvPath, ["========================================"])
		write_csv(csvPath, ["All File List"])
		write_csv(csvPath, ["========================================"])

		for i in range(len(fileList)):
			if fileList[i].is_file():
				#fileSize = os.path.getsize(filelist[i])
				fileSize = os.stat(str(fileList[i])).st_size
				if FILE_SIZE < 0:
					fileSize = -fileSize
				if fileSize >= FILE_SIZE:
					#fileTimeStamp = os.path.getctime(filelist[i])
					fileName = fileList[i].name
					filePath = str(fileList[i])
					fileExt  = fileList[i].suffix
					fileTimeStamp = os.stat(str(fileList[i])).st_ctime
					fileUid = os.stat(str(fileList[i])).st_uid
					fileMd5 = hash_md5(str(fileList[i]))
					fileListTable = [i, fileName, filePath, fileExt, fileSize,
									fileTimeStamp, fileUid, fileMd5]
					cursor.execute("INSERT INTO fileListTable VALUES (?,?,?,?,?,?,?,?)", fileListTable)
					write_csv(csvPath, fileListTable)
			view_progressbar(i+1, len(fileList))
	return True


#重複したファイルを削除する(同時にDBも更新)
def check_duplicate(dbPath, csvPath, deleteFlag):
	print("Start check_duplicate()")
	with sqlite3.connect(dbPath) as connection :
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM fileListTable")
		fileListTable = cursor.fetchall()

		#DBからファイルリストを取得する
		write_csv(csvPath, ["========================================"])
		write_csv(csvPath, ["Duplicate File"])
		write_csv(csvPath, ["========================================"])
		for i in range(len(fileListTable)):
			select_sql = "SELECT * FROM fileListTable WHERE file_md5 = '%s' " % fileListTable[i][7]
			cursor.execute(select_sql)
			tmp = cursor.fetchall()
			#先頭のファイルと被ったファイルを削除とDB更新
			for j in range(1, len(tmp)):
				if os.path.isfile(tmp[j][2]):
					write_csv(csvPath, tmp[j])
					cursor.execute(u"DELETE FROM fileListTable WHERE id=%s" % tmp[j][0])	
					if deleteFlag:
						os.remove(tmp[j][2])
			view_progressbar(i+1, len(fileListTable))
	return True

#コマンド引数解析
def get_option():
	argparser = ArgumentParser()
	argparser.add_argument('-d', '--Dir', type=str,
						   default="C:\\test",
						   help='target path')
	argparser.add_argument('-s', '--Size', type=int,
						   default="0",
						   help='file size + upper, - lower')
	argparser.add_argument('-f', '--DeleteFlag', type=bool,
						   default=False,
						   help='Do not delete files')
	arg = argparser.parse_args()
	return arg

#main
if __name__ == '__main__':
	#path = "C:\\test"
	args = get_option()
	targetPath = args.Dir
	FILE_SIZE = args.Size
	deleteFlag = args.DeleteFlag

	fileList = listup_files(targetPath)
	paths = make_path(targetPath)
	dbPath = paths[0]
	csvPath = paths[1]
	create_db(fileList, dbPath, csvPath)
	copy_file(dbPath)
	check_duplicate(dbPath, csvPath, deleteFlag)
	#for i in range(len(list)):
	#	print(list[i])
	
