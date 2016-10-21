from datetime import datetime

# source: http://stackoverflow.com/a/1835259/2812587
def is_sequence(arg):
    return (not hasattr(arg, "strip") and
            hasattr(arg, "__getitem__") or
            hasattr(arg, "__iter__"))


def debug_print(msg, *args):
	msg = '[{0}] {1}'.format(datetime.now(), msg)
	arg_list = []
	for a in args:
		if is_sequence(a):
			for i in a:
				arg_list.append(i)
		else:		
			arg_list.append(a)


	print(msg.format(*arg_list))