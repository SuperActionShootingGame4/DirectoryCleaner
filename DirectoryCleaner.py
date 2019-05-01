import glob
import os
import csv
from pathlib import Path
import sqlite3
from contextlib import closing
import hashlib
from argparse import ArgumentParser

dbname = 'test.db'

def write_csv(list):
	with open("C://test/abc.csv", 'a') as f:
		writer = csv.writer(f, lineterminator='\n') # 改行コード（\n）を指定しておく
		writer.writerow(list)     # list（1次元配列）の場合
	return True

#ファイルリスト作成
def listup_files(path):
    #yield [os.path.abspath(p) for p in glob.glob(path)]
	p = Path(path)
	return list(p.glob("**/*"))

#md5計算
def hash_md5(path):
	with closing(open(path, "rb")) as file:
		binary = file.read()
	return hashlib.md5(binary).hexdigest()

#db作成
def create_db(path, list):
	db_path = path + "\\" + dbname
	with closing(sqlite3.connect(db_path)) as conn:
		c = conn.cursor()
		#executeメソッドでSQL文を実行する
		create_table = '''create table flist ( id int, 
												filea_name varchar(256), 
												filea_path varchar(258), 
												file_ext varchar(256), 
												file_size int,
												file_time int, 
												file_md5 int )'''
		c.execute(create_table)
		sql = '''insert into flist (id,
									filea_name,
									filea_path,
									file_ext,
									file_size,
									file_time,
									file_md5) values (?,?,?,?,?,?,?)'''
		write_csv(["file list"])
		for i in range(len(list)):
			if list[i].is_file():
				file_size = os.path.getsize(list[i])
				if file_size <= 1000000:
					datetime = os.path.getctime(list[i])
					md5 = hash_md5(list[i])
					flist = (i, list[i].name, str(list[i]), list[i].suffix, 
							 file_size, datetime, md5)
					c.execute(sql, flist)
					write_csv(flist)
		check_duplicate(c)
		#conn.close()
	return

#重複チェック
def check_duplicate(c):
	select_sql = "SELECT * FROM flist"
	c.execute(select_sql)
	val = c.fetchall()
	print(val)
	print(type(val))
	print(val[0][6])
	write_csv(["remove file list"])
	for i in range(len(val)):
		select_sql = "SELECT * FROM flist WHERE file_md5 = '%s' " % val[i][6]
		c.execute(select_sql)
		tmp = c.fetchall()
		for j in range(1, len(tmp)):
			if os.path.isfile(tmp[j][2]):
				os.remove(tmp[j][2])
				c.execute(u"delete from flist where id=%s" % tmp[j][0])
				write_csv(tmp[j])
								
	return

def get_option():
	argparser = ArgumentParser()
	argparser.add_argument('-d', '--dir', type=str,
	                       default="C:\\test",
	                       help='target path')
	return argparser.parse_args()

if __name__ == '__main__':
	#path = "C:\\test"
	args = get_option()
	path = args.dir
	list = listup_files(path)
	create_db(path, list)
	#for i in range(len(list)):
	#	print(list[i])
	
