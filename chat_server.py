import select
import socket 
import sys
import Queue
from debug import debug_print
from chat_socket import chat_socket


# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)

# Bind the socket to the port
server_address = ('localhost', 10000)
debug_print('starting up on {0} port {1}', server_address)
server.bind(server_address)

# Listen for incoming connections
server.listen(5)

# Sockets from which we expect to read
inputs = [ server ]

# Sockets from which we expect to write
outputs = [ ]

# Outgoing messages queues (socket:Queue)
message_queues = {}

# Usernames for current socket sessions (socket:Name)
usernames = {}

while inputs:

	# Wait for at least one of the sockets to be ready for processing
	#debug_print('Waiting for the next event')
	readable, writeable, exceptional = select.select(inputs, outputs, inputs)

	# Handles inputs 
	for s in readable:

		if s is server:
			# A 'readable' server socket is ready to accept a new connection
			connection, client_address = s.accept()
			debug_print('new connection from {0}', client_address)
			connection.setblocking(0)
			inputs.append(connection)

			# Give the connection a queue for data we want to send
			message_queues[connection] = Queue.Queue()

		else:
			chat_sock = chat_socket(sock=s, blocking=False, debug=True)
			data = None

			try:
				data = chat_sock.read().strip()
				debug_print('received "{0}" from {1}', data, chat_sock.sock.getpeername())

				if s not in usernames:
					usernames[s] = data + ': '
					data += ' connected'
				else:
					data = usernames[s] + data

				for _, queue in message_queues.iteritems():
					queue.put(data)

				if s not in outputs:
					outputs.append(s)

				
			except:
				chat_sock.close()
				inputs.remove(s)
				outputs.remove(s)


	for s in writeable:
		try:
			next_msg = message_queues[s].get_nowait()
		except Queue.Empty:
			pass
			# No messages waiting to stop checking for writeability 
			#debug_print('output queue for {0} is empty', s.getpeername())
			#outputs.remove(s)
		else:
			debug_print('sending {0} to {1}', next_msg, s.getpeername())
			chat_sock = chat_socket(s)
			chat_sock.send(next_msg)
			try:
				pass
			except:
				debug_print('Unable to send via chat_socket')


	# Handle 'exceptional conditions'
	for s in exceptional:
		debug_print('handling exceptional condition for {0}', s.getpeername())
		# Stop listening for input on the connection
		inputs.remove(s)
		if s in outputs:
			outputs.remove(s)
		s.close()

		# Remove message queue
		del message_queues[s]











