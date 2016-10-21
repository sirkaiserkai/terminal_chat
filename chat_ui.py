from curses import wrapper
import select
import curses
import socket
import copy
from threading import Thread
from chat_socket import chat_socket
from debug import debug_print

RUN_SOCKET = True
msg_list = []

def main(stdscr):
	# Clear screen
	global RUN_SOCKET
	curses.halfdelay(1)
	msg_queue = []
	stdscr.clear()
	curses.noecho()
	stdscr.addstr(0,0, 'What up boi: Type your username and then get to chattin\'', curses.A_REVERSE)
	stdscr.refresh()
	height,width = stdscr.getmaxyx()

	stdscr.move(height-1, 0)
	sock_backend = Thread(target=run_chat_client, args=[stdscr, msg_queue])
	sock_backend.start()

	try:
		while True:
			c = stdscr.getch()
			stdscr.refresh()
			height,width = stdscr.getmaxyx()
			if c == -1:
				pass
			if c == curses.KEY_ENTER or c == 10 or c == 13:
				msg = stdscr.instr(height-1, 0)
				msg_queue.append(msg)
				#stdscr.addstr(0,0, msg, curses.A_REVERSE)
				stdscr.move(height-1, 0)
				stdscr.clrtoeol()
			elif c == curses.KEY_BACKSPACE or c == 127:
				y,x = stdscr.getyx()
				if x > 0:
					stdscr.addstr(height-1, x-1, ' ')
					stdscr.move(y, (x-1) % width)
			elif c == curses.KEY_LEFT:
				y, x = stdscr.getyx()
				stdscr.move(y, (x-1) % width)
			elif c == curses.KEY_RIGHT:
				y, x = stdscr.getyx()
				stdscr.move(y, (x+1) % width)
			elif c > 31 and c < 127:
				y,x = stdscr.getyx()
				if x < width - 1:
					stdscr.addstr(height-1, (x % width), chr(c))
					stdscr.move(y,(x+1) % width)


	except KeyboardInterrupt:
		RUN_SOCKET = False # In the ghettoooooo



def print_msgs(stdscr, new_msg, msg_list):
	if len(msg_list) == 0:
		 msg_list.append((new_msg, curses.A_REVERSE))
	else:
		if msg_list[len(msg_list)-1][1] != curses.A_REVERSE:
		 	msg_list.append((new_msg, curses.A_REVERSE))
		else:
		 	msg_list.append((new_msg, 0))

	height,width = stdscr.getmaxyx()
	if len(msg_list) > height-3:
		msg_list.pop(0)

	cpy_msg_list = copy.deepcopy(msg_list)

	for y in xrange(height-2):
		if len(cpy_msg_list) != 0:
			msg = cpy_msg_list.pop(0)
			stdscr.addstr(y, 0, ' ' * (width-1))
			stdscr.addstr(y, 0, msg[0], msg[1])
		else:
			stdscr.move(height-1, 0)
			break


def run_chat_client(stdscr, output_queue):
	global RUN_SOCKET, msg_list
	server_address = ('localhost', 10000)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	#debug_print('connecting to {0} port {1}', server_address)
	sock.connect(server_address)
	sock.setblocking(0)

	socks = [ sock ]

	while RUN_SOCKET:
		readable, writeable, exceptional = select.select(socks, socks, socks, 5)

		for s in readable:
			chat_sock = chat_socket(s)
			data = None
			try:
				data = chat_sock.read()
				#print(data + '\n')
				#stdscr.addstr(5,0, str(data), curses.A_REVERSE)
				print_msgs(stdscr, data, msg_list)
				#stdscr.addstr(0,0, str(data), curses.A_REVERSE)

			except Exception as inst:
				stdscr.addstr(5,0, str(inst), curses.A_REVERSE)					

		for s in writeable:
			try:
				while output_queue:
					next_message = output_queue.pop(0)
					chat_sock = chat_socket(s)
					chat_sock.send(next_message)
					writeable.remove(s)
			except:
				pass
			else:
				pass

		for s in exceptional:
			s.close()


	debug_print('Closing sockets')
	for sock in socks:
		sock.close()


wrapper(main)
