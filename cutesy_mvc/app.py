from .helpers.cutify import handleCuteness
from .helpers.client import Client
from .views.root import Root
import sys
import curses
import time 

def run():
	if len(sys.argv) > 2: 
		# cutesy command line service handler
		if sys.argv[1] == 'cutify':
			handleCuteness(sys.argv[2])
	else:
		curses.wrapper(main)

quit = False

def exit():
	global quit
	quit = True

def main(stdscr):
	curses.noecho()
	c = Client(lambda x: x)
	stdscr.clear()
	curses.curs_set(0)
	curses.halfdelay(1)
	dim = stdscr.getmaxyx()
	h = dim[0]
	w = dim[1]
	tlx = 0
	tly = 0
	win = curses.newwin(h, w, tly, tlx)
	win.box()
	win.keypad(True)
	global exit
	global quit

	l1 = "Apps by 'Veezy"
	l2 = "Copyright 2021"
	l3 = "Controls: WASD & Space"
	win.addstr(dim[0] // 2 - 1, dim[1] // 2 - 7, l1)
	win.addstr(dim[0] // 2, dim[1] // 2 - 7, l2)
	win.addstr(dim[0] // 2 + 1, dim[1] // 2 - 11, l3)
	win.refresh()
	time.sleep(5)
	curses.flash()
	win.clear()
	win.box()
	r = Root(props={'win': win, 'off': exit, 'writable': {
		'xmin': 1,
		'xmax': dim[1] - 1,
		'ymin': 1,
		'ymax': dim[0] - 1
	}})
	
	curses.flushinp()
	r.render()
	win.refresh()
	last = time.time()
	delta = 0
	while not(quit):
		delta = last - time.time()
		r.handleResponses()
		r.handleInput()
		r.render()
		last = time.time()
		win.refresh()
		win.box()
	del r

	c.shutdown()
