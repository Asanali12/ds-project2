from threading import Thread
import sys, os
import socket
import time
from pprint import pprint

HOST = ""							# Client Server IP address = 10.0.15.12
ss_ip = ""							# Storage Server IP address
ns_ip = "10.0.15.11"				# Naming Server IP address
port_send = 5500							# Naming/Storage/Host Server Port
port_recieve = 5100
ns_port = 5050


def create_socket(host):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port_send))
	return s


commands = ["help", "init", "create_file",
			"read_file", "write", "delete_file",
			"info", "copy", "move", "open", "read",
			"create_directory", "delete_directory" "exit"]


def check_command(command):
	splitted = command.split()
	lenth = len(splitted)

	if splitted[0] not in commands:
		print("Incorrect command")
		return -1

	else:
		if lenth == 1:
			if splitted[0] != 'help' and splitted[0] != 'init' and splitted[0] != "exit": 
				print("Incorrect command")
				return -1

		elif lenth == 2:
			if splitted[0] != "create_file" and splitted[0] != "read_file" and \
				splitted[0] != "write" and splitted[0] != "delete_file" and \
				splitted[0] != "info" and splitted[0] != "copy" and \
				splitted[0] != "open" and splitted[0] != "read" and \
				splitted[0] != "create_directory" and splitted[0] != "delete_directory":
				print("Incorrect command")
				return -1

		elif lenth == 3:
			if splitted[0] != "move":
				print("Incorrect command")
				return -1

		else:
			print("Incorrect command")
			return -1
	return 1


def change_name(name):                                      		#function for changing the name of the file
    if os.path.exists(name):                                        #in case file with such a name exists we change its name
        i = 1
        new_name=name
        while os.path.exists(new_name):
            if "." in name:                                         #splitting the filename by '.' symbol if it has an extension
                no_ext = "".join(name.split(".")[:-1])              #inserting '_c' mark before extension
                ext = name.split(".")[-1]
                new_name = no_ext+"_c"+str(i)+"."+ext
            else:
                new_name = no_ext+"_c"+str(i)                       #just adding '_c' mark in case if ther is no extension
            i += 1
        return new_name
    else:
        return name


def help():
    print(
    	"Commands and arguments:\n"
    	"help                                   : \n"
        "init                                   : \n"
		"create_file <directory>                : \n"
		"read_file <directory>                  : \n"
		"write <directory>                      : \n"
		"delete_file <directory>                : \n"
		"info <directory>                       : \n"
		"copy <directory>                       : \n"
		"move <source> <destination>            : \n"
		"open <directory>                       : \n"
		"read <directory>                       : \n"
		"create_directory <directory>           : \n"
		"delete_directory <directory>           : \n"
		"exit                                   : \n"
    )



def make_connection():
	# s = create_socket(ns_ip)

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

	# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((ns_ip, ns_port))
		s.send("start".encode())
		s.close()

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST, port_recieve))
		s.listen(1)
		for patience in range(10):
			(storage_socket, address) = s.accept()
			print(".", end='')
			response = ""
			response = storage_socket.recv(1024).decode()

			if response != "":
				s.close()
				print("\nIP address of Storage Server is recieved: ", end='')
				return response

			time.sleep(1)

		print("Naming Server is not responding :(")
		return "-1"


def send_file(directory, s):
	directory = directory.split("/")
	file_name = directory[-1]

	s.sendall(str(file_name).encode())                      #send the file

	actual = os.path.getsize(name)                          #getting the size of the file
	sending = 0                                             #already sent data

	with open(name, "rb") as file:                          #opening file
		while True:
			buff = file.read(1024)                          #reading the file
			if not buff:
				break

			s.sendall(buff)                              	#sending the data
			sending = sending + len(buff)                   #checking the amount sent

	print("Successfully sent the file!\n")


def recieve_file(directory):
	directory = directory.split("/")
	file_name = directory[-1]

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.bind((HOST, port_recieve))
		storage_socket, addr = s.accept()
		with open(file_name, "wb") as file:                              #recieving data and writing it
			while True:
				data = storage_socket.recv(1024).decode()
				if not data:
					break
				file.write(data)
	print("File is recieved\n")


def client_app():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ss_ip, port_send))
	ss.bind((HOST, port_recieve))
	print("Connetction estabilished!\n")

	while True:

		command = input("\nEnter your command: ")
		
		s.sendall(str(command).encode())

		validance = check_command(str(command))
		if validance == -1:
			continue

		splitted = str(command).split()
		lenth = len(splitted)

		if splitted[0] == "exit":
			print("Session is ended!\nGood bye!")
			s.close()
			break

		if splitted[0] == "write":
			send_file(splitted[1], s)
			continue

		elif splitted[0] == "read_file":
			recieve_file(splitted[1])
			continue

		elif splitted[0] == "help":
			help()
			continue

		else:
			
			
			ss.listen(1)
			responsed = False
			for patience in range(10):
				(storage_socket, address) = ss.accept()
				response = storage_socket.recv(1024).decode()

				if response:
					pprint(response)
					responsed = True
					break

				time.sleep(1)

			if not responsed:
				print("Storage Server is not responding :(\nTry again\n")

if __name__ == "__main__" :
	help()

	while True:
		ss_ip = make_connection()
		if ss_ip == '':
			var = input("Do you want to try again? [y/n]: ")
	
			if var == "n":
				break
		else :
			print(ss_ip)
			client_app()
			break
	# if ss_ip != '' and ss_ip != "-1":
	# 	client_app()
