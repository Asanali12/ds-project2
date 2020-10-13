from threading import Thread
import socket

class NamingServer:

	_storages=[]
	_ready=[]


	def __init__(self, servers):
		_storages=servers
		self.ping_all()


	def change_name(name):
		if os.path.exists(name):
			i = 1
			new_name=name
			while os.path.exists(new_name):
				if "." in name:
					no_ext = "".join(name.split(".")[:-1])
					ext = name.split(".")[-1]
					new_name = no_ext+"_c"+str(i)+"."+ext
				else:
					new_name = no_ext+"_c"+str(i)
				i += 1
			return new_name
		else:
			return name

	def ping_all(self):
		self._ready=[]
		for i in range(len(self._storages)):
			self._ready.append(ping_one(_storages[i]))


	def ping_one(addr):
		resp = os.system("ping -c 1 " + addr)
		if resp == 0:
			return True
		else:
			return False

	def send_ip(self, addr, port):
		self.ping_all()
		available=[]
		for i in range(len(self._storages)):
			if self._ready[i] == True:
				available.append(self._storages[i])
		ip = available[0]
		#ip = "10.0.15.10"
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
			sock.connect((addr, port))
			sock.send(ip.encode())


	def decode_message(self, con, addr):
		data = "-a-a-a-"
		with con:
			print("Receiving from ", addr)
			while True:
				
				d = con.recv(1024).decode()
				if not d:
					break
				data = d
			print("Message is recieved")

		print(data)
		data=data.split(" ")
		if data[0] == "start":
			self.send_ip(addr[0], 5100)
		else:
			print("No such command\n")


HOST = ""


if __name__ == "__main__":
	srv = NamingServer([""])
	port = 5001
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
		sock.bind((HOST, 5050))
		while True:
			sock.listen(1)
			con, addr = sock.accept()
			thread = Thread(target=srv.decode_message, args=(con, addr))
			thread.start()
