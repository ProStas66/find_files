#!/usr/bin/python3

import os
import sqlite3 as s1
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import *
from pathlib import Path
from pathlib import PurePath
import shutil
import configparser
from PIL import Image, ImageTk
import subprocess
"""

"""

configfile = 'ff.ini'

conf = configparser.ConfigParser()
conf.read(configfile)

F_TYPE = conf['file_type']['ft'].split(', ')
PATH_NAME = conf['path_name']
host = conf['pathes']['host']
PATH_N = Path(conf['pathes']['path_n'])
PATH_X = Path(conf['pathes']['path_x'])

def ping(ip):
	retcode = subprocess.call('ping -n 1 ' + str(ip))
	if retcode != 0:
		messagebox.showerror('Ошибка запроса', 'Нет связи с сервером')
	else:
		main_win(window)

class db:
	def __init__(self):
		self.con = s1.connect('makets.db')
		self.cursor = self.con.cursor()

	
	def insert(self, sql, data):
		self.cursor.executemany(sql, data)
		self.con.commit()


	
	def query(self, ql):
		self.cursor.execute(ql)
		self.con.commit()


	
	def query_read(self, ql):
		result = None
		self.cursor.execute(ql)
		result = self.cursor.fetchall()
		return result
	
	def __del__(self):
		self.con.close()

class main_win:
	
	def __init__(self, master):
		self.master = master
		self.master.title('Поиск файлов')
		self.master.iconbitmap('ff.ico')
		
		self.f_find = Frame()
		self.f_find.pack()
		self.combo_type = Combobox(self.f_find, width=10,
						values=F_TYPE)
		self.combo_type.current(0)
		self.combo_type.pack(side=TOP, anchor=W)
		self.combo_table = Combobox(self.f_find, width=10,
						values=settings.list_tables(self),
						state='readonly')
		self.combo_table.current(0)
		self.combo_table.pack(side=LEFT)
		self.e_file = Entry(self.f_find, width = 20)
		self.e_file.focus()
		self.e_file.pack(side=LEFT)
		self.btn_file = Button(self.f_find, text='Найти файл', 
						command=self.list_files)
		self.btn_file.pack(side=LEFT)
		self.btn_copy = Button(self.f_find, text='Копировать файл', 
						command=self.copy_file)
		self.btn_copy.pack(side=LEFT)
		self.set_ico = PhotoImage(file='settings-14.png')
		self.set_ico_resize = self.set_ico.subsample(1, 1)
		self.btn_set = Button(self.f_find, image=self.set_ico_resize, 
						command=self.open_settings)
		self.btn_set.pack(side=LEFT)
		
		self.tb_files = Treeview(show='headings', columns=('file', 'path'))
		self.tb_files.heading('#1', text='file')
		self.tb_files.heading('#2', text='path')
		self.tb_files.bind("<<TreeviewSelect>>", self.change_prew)
		self.tb_files.pack()
		self.open_prew()
		self.close_prew()
		self.master.mainloop()
		
	
	def pozicion(self):
		poz = self.master.geometry()
		poz = poz.split('+')
		poz = poz[1:]
		poz[0] = int(poz[0]) + 225
		return poz
	
	def get_value(self):
		formats = ('jpg', '.gif', '.png', '.tif', '.psd', '.eps')
		file_path = 'no_file.jpg'
		if self.select_row():
			file_path = self.select_row()[0]
			path_end = ''
			if  str(file_path).endswith('.cdr'):
				file_path = self.ch_type(file_path)

			elif str(file_path).endswith(formats):
				file_path = self.select_row()[0]
			else:
				file_path = 'no_image.png'
		return file_path
	
	def ch_type(self, fpath):
		file_type = ['.jpg', '.eps']
		file_dir = fpath.parent
		file_name = fpath.stem
		for t in file_type:
			name = file_name + t
			file_path = file_dir / name
			if Path.is_file(file_path):
				break
			else:
				file_path = 'corel_file.png'
		return file_path
		
	def open_prew(self):
		self.poz = self.pozicion()
		if self.get_value():
			self.send_value = self.get_value()
		else:
			self.send_value = 'no_file.jpg'
		self.thumbnail = preview(self.master, self.poz, self.send_value)
	
	def close_prew(self):
		self.thumbnail.cls()
	
	def change_prew(self, event):
		self.close_prew()
		self.open_prew()
	
	def open_settings(self):
		self.close_prew()
		self.poz = self.pozicion()
		self.set = settings(self.master, self.poz).update_data()


	
	def sql_read(self, table, file_name, file_type):
		zapros = f"""SELECT file, path FROM {table} 
				WHERE file GLOB '{file_name}*{file_type}'"""
		return zapros
	
	def list_files(self):
		table = self.combo_table.get()
		file_name = self.e_file.get()
		file_type = self.combo_type.get()
		self.tb_files.delete(*self.tb_files.get_children())
		zapros = self.sql_read(table, file_name, file_type)
		maket = makets.query_read(zapros)
		for i in maket:
			self.tb_files.insert('', 0, values=i)
	
	def select_row(self):
		selected = []
		for select in self.tb_files.selection():
			item = self.tb_files.item(select)
			file_path = Path(PATH_N / item['values'][1] / item['values'][0])
			selected.append(file_path)
		return selected
	
	def copy_file(self):
		selected = self.select_row()
		for file_path in selected:
			shutil.copy2(file_path, PATH_X)


class settings:
	
	def __init__(self, master, poz):
		self.set = Toplevel(master)
		self.set.title('Настройки')
		self.set.geometry('+{}+{}'.format(str(poz[0]+200), poz[1]))
		self.f_set = LabelFrame(self.set, text='Настройки базы данных')
		self.f_set.pack(side=BOTTOM, fill=X)
		self.l_table_name = Label(self.f_set, text="Имя таблмцы")
		self.l_table_name.pack(side=LEFT)
		self.combo_table = Combobox(self.f_set, values=[option for option in PATH_NAME])
		self.combo_table.pack(side=LEFT)
		self.btn_create_table = Button(self.f_set, text='Создать таблицу', 
								command=self.create_table)
		self.btn_create_table.pack(side=LEFT)
		self.btn_ins_data = Button(self.f_set, width=16, 
						text='Загрузить данные', command=self.insert_btn)
		self.btn_ins_data.pack()
		self.btn_del_data = Button(self.f_set, width=16, 
						text='Очистить таблицу', command=self.clear_table)
		self.btn_del_data.pack(side=BOTTOM, anchor=E)
		self.btn_del_dables = Button(self.f_set, width=16, 
						text='Удалить дубли', command=self.del_copies)
		self.btn_del_dables.pack(side=BOTTOM, anchor=E)

		
	def update_data(self):
		table = 'cdrs_work'
		path = PATH_NAME[table]
		dirs = os.listdir(path)
		path = path + '\\' + max(dirs)
		self.insert_data(table, path)
		self.del_copies(table)
		
		
	def insert_btn(self):
		table = self.table_name()
		path = PATH_NAME[table]
		self.insert_data(table, path)
		self.del_copies(table)
		
	def table_name(self):
		name = self.combo_table.get()
		if name == '':
			messagebox.showerror('Ошибка запроса', 'Не выбрана таблица')
			raise IndexError("index out of range")
		else:
			return name
	
	def walk_dir(self, paths):
		tree = os.walk(paths)
		ff = []
		for d, dirs, files in tree:
			for f in files:
				d = Path(d)
				below_d = str(d.relative_to(Path(PATH_N)))
				para = (f, below_d)
				ff.append(para)
		return(ff)
	
	def create_table(self):
		name = self.table_name()
		zapros = f"""
			CREATE TABLE {name}(
			id integer not null primary key autoincrement,
			file text,
			path text
			);"""
		makets.query(zapros)
	
	def list_tables(self):
		zapros = 'SELECT name FROM sqlite_master WHERE type="table";'
		spisok = makets.query_read(zapros)
		values = []
		for i in spisok:
			j = [i][0][0]
			if j != 'sqlite_sequence':
				values.append(j)
		if values == []:
			values = ['нет таблиц']
		return values
	
	def insert_data(self, table, path):
		zapros = f'INSERT INTO {table} (file, path) values(?, ?)'
		data = self.walk_dir(path)
		makets.insert(zapros, data)
		messagebox.showinfo('Список файлов', f'В таблицу {table} добавлены данные')
			
	def del_copies(self, table):
		zapros = f"""DELETE FROM {table} 
			WHERE id NOT IN (SELECT min(id) as MinRowID 
			FROM {table} GROUP BY file, path)"""
		makets.query(zapros)
		#messagebox.showinfo('Список файлов', 'Удалены дубликаты записей')
	
	def clear_table(self):
		table = self.table_name()
		zapros = f'DELETE FROM {table}'
		makets.query(zapros)
		messagebox.showinfo(f'Таблица {table}', 'Данные удалены')
		

class preview:
	
	def __init__(self, master, poz, fpath=''):
		self.prew = Toplevel(master)
		self.prew.title(fpath)
		self.prew.overrideredirect(True)
		self.prew.geometry('+{}+{}'.format(str(poz[0]+200), poz[1]))
		self.lbl = Label(self.prew)
		try:
			self.src_img = Image.open(fpath)
		except:
			self.src_img = Image.open('no_image.png')
		
		# размер картинки		

		razmer = self.src_img.size
		koef = max(razmer) // 500 + 1
		self.src_img = self.src_img.resize((razmer[0]//koef, razmer[1]//koef ))
		
		self.img = ImageTk.PhotoImage(self.src_img)
		self.lbl['image'] = self.img
		#self.lbl.image=self.img
		self.lbl.pack()
	
	def cls(self):
		self.prew.destroy()

	

makets = db()
window = Tk()
ping(host)

#main_win(window)

