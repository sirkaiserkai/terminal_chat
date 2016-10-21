import socket
import time
from debug import debug_print

BUFFER_SIZE = 2048

class chat_socket:
	
	def __init__(self, sock=None, blocking=True, debug=False):
		if sock is None:
			sock = socket.socket(
				socket.AF_INET, socket.SOCK_STREAM)
		
		self.sock = sock
		self.blocking = blocking
		self.sock.setblocking(blocking)
		self.debug = debug
		self._debug('Created new socket')

	def _debug(self, msg, *args):
		if self.debug:
			debug_print(msg, args)

	def connect(self, *args):
		self.sock.connect(*args)

	def close(self):
		try:
			self._debug('Closing socket: {0}', self.sock.getpeername())
			self.sock.shutdown(1)
		except:
			self._debug('Sloppy socket close ')

		if self.sock != None:
			self.sock.close()
			self.sock = None

	def send(self, msg):
		self._debug('Sending from socket: {0}', self.sock.getpeername())
		total_sent = 0
		msg_length = len(msg)
		if len(str(len(msg))) > 5:
			raise RuntimeError('Message size too long')

		formatted_size = str(len(msg)).zfill(5)
		msg = '{0}{1}'.format(formatted_size, msg)

		while total_sent < msg_length:
			sent = self.sock.send(msg[total_sent:])
			self._debug('{0} sent: {1}', self.sock.getpeername(), sent)

			if sent == 0:
				raise RuntimeError('socket connection broken')

			total_sent += sent

	def read(self):
		global BUFFER_SIZE
		chunks = []
		bytes_recd = 0
		msg_length = '' # Must be converted from string -> num

		timout = time.time() + 60*5

		# Loops through beginning of message to retrieve 
		# message length: example format: '00011hello world'
		while True:
			chunk = self.sock.recv(5)
			if not chunk:
				self.close()
				raise RuntimeError('socket connection broken unable to read')
				return

			msg_length = msg_length.join(chunk)

			if len(msg_length) == 5:
				break

			if time.time() > timout:
				self.close()
				raise RuntimeError('socket connection broken unable to read')
				return



		try:
			msg_length = int(msg_length)
		except:
			raise RuntimeError('socket message was not prefaced with message size')

		while bytes_recd < msg_length:
			chunk = self.sock.recv(min(msg_length - bytes_recd, BUFFER_SIZE))
			if not chunk:
				raise RuntimeError('socket connection broken')

			chunks.append(chunk)
			bytes_recd += len(chunk)

		#return (msg_length, ''.join(chunks))
		return ''.join(chunks)





