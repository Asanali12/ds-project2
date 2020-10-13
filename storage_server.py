import os
import shutil
from threading import Thread
import sys, os
import socket
import time
from pprint import pprint
from queue import Queue

HOST = ""
port_send = 5100							# Naming/Storage/Host Server Port
port_recieve = 5500

class StorageServer(object):
	
	_files=[]
	directory=""
	_max=0

	def __init__(self):
		self.directory = os.getcwd()
		self._max = 268435456
		try:
			os.mkdir(self.directory)
			self._files = []
		except FileExistsError:
			self._files, size = self.__get_info()
			if self._max < size:
				raise AttributeError
			self._max -= size

	def __len__(self) -> int:
		l = len(self._files)
		return l

	def __contains__(self, path: str) -> bool:
		try:
			self._files.index(path)
			return True
		except ValueError:
			return False

	def __iter__(self):
		return self._files.__iter__()

	def __setitem__(self, source: str, destination: str) -> None:
		i = self._files.index(source)
		self._files[i] = destination

	def __get_info(self) -> tuple:
		q = Queue()
		s = 0
		file_names = []
		for sub_path in os.listdir(self.directory):
			real_path = self.directory+"/"+sub_path
			if os.path.isdir(real_path):
				q.put(sub_path)
			else:
				file_names.append(sub_path)
				s += os.path.getsize(real_path)
		while not q.empty():
			next_path = q.get()
			real_directory = self.directory+"/"+next_path
			for d in os.listdir(real_directory):
				next_p = next_path+"/"+d
				if os.path.isdir(next_p):
					q.put(next_p)
				else:
					file_names.append(next_p)
					s += os.path.getsize(next_p)
		return file_names, s

	def check_directory(self, d:str)->bool:
		if d in self._files:
			return True
		else:
			return False

	def open_directory(self, path:str):
		self.directory = self.directory+"/"+path
		return ("done")

	def delete_directory(self, path:str):
		shutil.rmtree(self.directory+"/"+path)
		return("done")

	def read_directory(self, path:str):
		return os.walk(self.directory+"/"+path)

	def copy_file(self, source:str):
		shutil.copyfile(source, source)
		return("done")

	def file_read(self, path:str)->bytes:
		real_path = self.home_path + path
		f = open(real_path, "r");
		return f.read()

	def file_write(self, path:str, data:bytes):
		real_path = self.home_path + path
		f = open(real_path, "w");
		f.write(data)
		self._files.append(path)
		return ("done")

	def create_path(self, path:str):
		if os.isdir(self.directory+"/"+path) == False:
			os.mkdir(self.directory+"/"+path)
		return ("done")

	def create_file(self, path:str, data:bytes):
		real_path = self.home_path + path
		self.create_path(real_path)
		f = open(real_path, "w");
		f.write(data)
		self._files.append(path)
		return ("done")

	def delete_file(self, path:str):
		real_path = self.home_path + path
		os.remove(real_path)
		self._files.remove(path)
		return ("done")

	def get_file_info(self, path:str)->tuple:
		real_path = self.home_path + path
		return os.stat(real_path)

	def move(self, source: str, destination: str):
		real_source = self.home_path + source
		real_destination = self.home_path + destination
		self.create_path(real_destination)
		shutil.move(real_source, real_destination)
		self[real_source] = dest_path
		self.clear_path(src_storage_path)
		return ("done")
	
	def check_command(self, command:str):
		cmd=command.split(" ")
		
		if cmd[0] == "create_file":
			return self.create_file(cmd[1])
		if cmd[0] == "read":
			if self.check_directory(cmd[1]):
				return self.file_read(cmd[1])
		if cmd[0] == "write":
			if self.check_directory(cmd[1]):
				return self.file_write(cmd[1], None)
		if cmd[0] == "delete_file":
			if self.check_directory(cmd[1]):
				return self.delete_file(cmd[1])
		if cmd[0] == "info":
			if self.check_directory(cmd[1]):
				return self.get_file_info(cmd[1])
		if cmd[0] == "copy":
			if self.check_directory(cmd[1]):
				return self.copy_file(cmd[1])
		if cmd[0] == "move":
			if self.check_directory(cmd[1]) and self.check_directory(cmd[2]):
				return self.move(cmd[1], cmd[2])
		if cmd[0] == "open":
			if self.check_directory(cmd[1]) :
				return self.open_directory(cmd[1])
		if cmd[0] == "read":
			if self.check_directory(cmd[1]) :
				return self.read_directory(cmd[1])
		if cmd[0] == "create_directory":
			self.create_path(cmd[1])
		if cmd[0] == "delete_directory":
			if self.check_directory(cmd[1]):
				return self.delete_directory(cmd[1])


def recieve_command(s):
	(client_socket, address) = s.accept()
	command = client_socket.recv(1024).decode()
	return (address[0], command)

def send_response(address, ss, resp):
	ss.connect((address, port_send))
	ss.sendall(resp)
	ss.close()

def storage_app():
	store = StorageServer()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, port_recieve))
	s.listen(5)
	ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	while True:
		pprint("Waiting for command...")
		(address, command) = recieve_command(s)
		response = store.check_command(command)
		send_response(address, ss, response)

if __name__ == "__main__":
	storage_app()