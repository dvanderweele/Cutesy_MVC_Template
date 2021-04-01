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
	h = 11
	w = 36
	tlx = 0
	tly = 0
	win = curses.newwin(h, w, tly, tlx)
	win.box()
	# writable x range = 1 - 34
	# writable y range = 1 - 9
	global exit
	global quit
	r = Root(props={'win': win, 'off': exit, 'writable': {
		'xmin': 1,
		'xmax': 34,
		'ymin': 1,
		'ymax': 9
	}})
	
	r.render()

	last = time.time()
	delta = 0
	while not(quit):
		delta = last - time.time()
		r.handleResponses()
		r.handleInput()
		r.render()
		last = time.time()
		win.refresh()
	del r

	c.shutdown()

	stdscr.getch()

