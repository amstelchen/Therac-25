import os
import sys
import curses
import string
from time import time, localtime, strftime
from datetime import date
from random import randint
import logging

LEFT	= 10
CENTER_LEFT	= 33
CENTER_RIGHT	= 50
RIGHT	= 70
CURMAX	= 13

BEAM_TYPES = ["","X","E"]
MODE_TYPES= ["DATA ENTRY","BEAM READY"]
actualbeam,beam,energy = 0, 0, 0
actual = [0.0,200,0.27,0.0,359.2,14.2,27.2,1,0]
prescribed = [0.0,0.0,0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
cloc=0
name = ""
done = 0
mode = 0
lastcheck = 0

curline = [1,2,2,5,6,7,10,11,12,13,14,15,22]
curcol = [16,CENTER_LEFT+11,RIGHT,CENTER_RIGHT,CENTER_RIGHT,CENTER_RIGHT,
		CENTER_RIGHT,CENTER_RIGHT,CENTER_RIGHT,CENTER_RIGHT,CENTER_RIGHT,
		CENTER_RIGHT,CENTER_RIGHT+9]

def main():
    global done
    logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    w = curses.initscr()
    curses.nonl()
    w.keypad(True)
    curses.cbreak()

    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1,curses.COLOR_GREEN,curses.COLOR_BLACK)
        w.attrset(curses.color_pair(1))
        w.bkgdset(curses.color_pair(1))
        w.clear()

    actualbeam = 0
    beam = 0
    energy = 0
    #*name=0
    mode = 0
    done=0
    cloc = 0
    lastcheck = 0

    while not done:
        display(w)
        getinput(w)

    return curses.endwin()

def display(w):

    global actual, prescribed, name, actualbeam, energy

    w.box(0,0)
    w.addstr(1,2,"PATIENT NAME: %s" % (name))
    w.addstr(2,2,"TREATMENT MODE: FIX")
    w.addstr(2,CENTER_LEFT,"BEAM TYPE: %s" % (BEAM_TYPES[actualbeam]))
    w.addstr(2,CENTER_RIGHT,"ENERGY (KeV):")
    w.addstr(2,RIGHT,"%d" % (energy))
    
    w.addstr(4,CENTER_LEFT,"ACTUAL")
    w.addstr(4,CENTER_RIGHT,"PRESCRIBED")
    w.addstr(5,LEFT,"UNIT RATE/MINUTE")
    w.addstr(6,LEFT,"MONITOR UNITS")
    w.addstr(7,LEFT,"TIME(MIN)")

    w.addstr(10,2,"GANTRY ROTATION (DEG)")
    w.addstr(11,2,"COLLIMATOR ROTATION (DEG)")
    w.addstr(12,2,"COLLIMATOR X (CM)")
    w.addstr(13,2,"COLLIMATOR Y (CM)")
    w.addstr(14,2,"WEDGE NUMBER")
    w.addstr(15,2,"ACCESSORY NUMBER")

    for i in range(9):
        w.addstr(5+i+(2 if i >= 3 else 0),CENTER_LEFT,"%10f" % (actual[i]))
        w.addstr(5+i+(2 if i >= 3 else 0),CENTER_RIGHT,"%10f" % (prescribed[i]))
        if i >= 3:
            w.addstr(10+i-3,RIGHT,"VERIFIED" if actual[i] == prescribed[i] else "")

    d = date.today()
    w.addstr(20,2,"DATE: %s" % (d))
    t = localtime()
    tmp = strftime("%T", t)
    w.addstr(21,2,"TIME: %s" % (tmp))
    w.addstr(22,2,"OPR ID: 033-%s" % (os.getenv("USER")))

    w.addstr(20,CENTER_LEFT-9,"SYSTEM: %s" % (MODE_TYPES[mode]))
    w.addstr(21,CENTER_LEFT-9,"TREAT: TREAT PAUSE")
    w.addstr(22,CENTER_LEFT-9,"REASON: OPERATOR")

    w.addstr(20,CENTER_RIGHT,"OP.MODE: TREAT\tAUTO")
    w.addstr(21,CENTER_RIGHT+9,"X-RAY\t173777")
    w.addstr(22,CENTER_RIGHT,"COMMAND: ")

    #w.addstr(1,RIGHT,"%d",cloc)
    w.move(curline[cloc],curcol[cloc])

    w.refresh()


def getinput(w):
    global cloc, prescribed, actual, done, actualbeam, name, energy
    origcloc = cloc

    curses.halfdelay(5)
    curses.noecho()
    c = w.getch()
    curses.echo()
    #curses.nocbreak()
    
    if c == curses.KEY_ENTER:
        if cloc > 5 and cloc < 12:
            prescribed[cloc-3] = actual[cloc-3] # copy
        if cloc < CURMAX-1:
            cloc += 1
    elif c == curses.KEY_UP:
        if cloc > 0:
            cloc -= 1
    elif c == curses.KEY_DOWN:
        if cloc < CURMAX-1:
            cloc += 1
    elif c == curses.ERR:
        pass # do nothing
    else:
        curses.ungetch(c)
        if cloc == 0:
            #if (scanw("%s" % (name)) != curses.ERR):
            name = w.getstr(15).decode('ascii')
            if name != curses.ERR:
                w.addstr(curline[cloc], curcol[cloc], name)
                cloc += 1  
        elif cloc == 1:
            c = chr(w.getch())
            w.addstr(c)
            if c == 'X' or c == 'x':
                actualbeam = 1
            elif c == 'E' or c == 'e':
                actualbeam = 2
            else:
                actualbeam = 0
                cloc += 1  
        elif cloc == 2:
            #if (scanw("%d" % (energy)) != curses.ERR):
            try:
                energy = int(w.getstr(15).decode('ascii'))
            except:
                pass
            if energy != curses.ERR:
                w.addstr(curline[cloc], curcol[cloc], str(energy))
                cloc += 1  
        elif cloc < 12:
            #if (scanw("%lg" % (prescribed[cloc-3])) != curses.ERR):
            try:
                prescribed[cloc-3] = float(w.getstr(15))
            except:
                pass
            if prescribed[cloc-3] != curses.ERR:
                w.addstr(curline[cloc], curcol[cloc], str(prescribed[cloc-3]))
                cloc += 1  
        else:
            c = chr(w.getch())
            w.addstr(str(c))
            if c == 'q' or c == 'Q':
                done = 1
                #sys.exit()
            if c == 'b' or c == 'B':
                doBeam()
    w.move(curline[origcloc],curcol[origcloc])
    w.clrtoeol()

    computeMode()
    
def computeMode():
    global lastcheck, prescribed, actual, beam, actualbeam, energy, mode
    t = time()
    if lastcheck > 0:
        if t-lastcheck < 8:
            return # take 8 sec to notice

    mode = len(name) > 0 and beam > 0 and energy > 0  # initial fields set
    for i in range(3, 9):
        mode = mode and actual[i] == prescribed[i]        # params match
    mode = mode and cloc == CURMAX-1                    # cursor on bottom line
    if mode:
        mode = 1
        lastcheck = t
    else:
        mode = 0
        lastcheck = 0
    beam = actualbeam

def doBeam():
    global mode, beam, actualbeam
    w2 = curses.newwin(3,50,12,15)
    w2.box(0,0)
    if mode == 0:
        w2.addstr(1,2,"MALFUNCTION 13 (Data entry incomplete)")
    else:
        if actualbeam == beam:
            w2.addstr(1,2,"TREATED %s SUCCESSFULLY!" % (name))
        elif actualbeam == 2:
            w2.addstr(1,2,"MALFUNCTION 54 (%d rads delivered)" % (randint(10000, 20000))) # (rand()%10000+10000))
        else:
            w2.addstr(1,2,"MALFUNCTION 26 (%d rads delivered)" % (randint(10, 20))) # (rand()%10+10))
    w2.refresh()
    curses.cbreak()
    w2.getch()
    #curses.delwin(w2)
    #touchwin(curscr)
    w2.refresh()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        curses.endwin()
        print("Therac-25 shutdown. 6 lives were saved.")
        sys.exit()
