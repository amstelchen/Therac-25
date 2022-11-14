#include <stdio.h>
#include <stdlib.h>
#include <curses.h>
#include <string.h>
#include <time.h>

#define LEFT 10
#define CENTER_LEFT 33
#define CENTER_RIGHT 50
#define RIGHT        70
#define CURMAX 13

char *BEAM_TYPES[] = {"","X","E"};
char *MODE_TYPES[]= {"DATA ENTRY","BEAM READY"};
int actualbeam,beam,energy;
double actual[] = {0.0,200,0.27,0.0,359.2,14.2,27.2,1,0};
double prescribed[] = {0.0,0.0,0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0};
int cloc=0;
char name[50];
int done;
int mode;
time_t lastcheck;

int curline[] = {1,2,2,5,6,7,10,11,12,13,14,15,22};
int curcol[] = {16,CENTER_LEFT+11,RIGHT,CENTER_RIGHT,CENTER_RIGHT,CENTER_RIGHT,
		CENTER_RIGHT,CENTER_RIGHT,CENTER_RIGHT,CENTER_RIGHT,CENTER_RIGHT,
		CENTER_RIGHT,CENTER_RIGHT+9};

void display(WINDOW *w);
void getinput(WINDOW *w);
void computeMode(void);
void doBeam(void);

int main(int argc, char **argv) {
  WINDOW *w;

  w = initscr();
  nonl();
  keypad(stdscr,TRUE);
  cbreak();

  if (has_colors()) {
    start_color();
    init_pair(1,COLOR_GREEN,COLOR_BLACK);
    attrset(COLOR_PAIR(1));
    bkgdset(' ' | COLOR_PAIR(1));
    clear();
  }

  actualbeam = 0;
  beam = 0;
  energy = 0;
  *name=0;
  mode = 0;
  done=0;
  cloc = 0;
  lastcheck = 0;

  while (!done) {
    display(w);
    getinput(w);
  }

  return endwin();
}

void display(WINDOW *w) {
  int i;
  time_t t;
  char tmp[50];
  char *ct;

  box(w,0,0);
  mvprintw(1,2,"PATIENT NAME: %s",name);
  mvprintw(2,2,"TREATMENT MODE: FIX");
  mvprintw(2,CENTER_LEFT,"BEAM TYPE: %s",BEAM_TYPES[actualbeam]);
  mvprintw(2,CENTER_RIGHT,"ENERGY (KeV):");
  mvprintw(2,RIGHT,"%d",energy);
  
  mvprintw(4,CENTER_LEFT,"ACTUAL");
  mvprintw(4,CENTER_RIGHT,"PRESCRIBED");
  mvprintw(5,LEFT,"UNIT RATE/MINUTE");
  mvprintw(6,LEFT,"MONITOR UNITS");
  mvprintw(7,LEFT,"TIME(MIN)");

  mvprintw(10,2,"GANTRY ROTATION (DEG)");
  mvprintw(11,2,"COLLIMATOR ROTATION (DEG)");
  mvprintw(12,2,"COLLIMATOR X (CM)");
  mvprintw(13,2,"COLLIMATOR Y (CM)");
  mvprintw(14,2,"WEDGE NUMBER");
  mvprintw(15,2,"ACCESSORY NUMBER");

  for (i=0; i < 9; i++) {
    mvprintw(5+i+(i >= 3 ? 2 : 0),CENTER_LEFT,"%10f",actual[i]);
    mvprintw(5+i+(i >= 3 ? 2 : 0),CENTER_RIGHT,"%10f",prescribed[i]);
    if (i >= 3)
      mvprintw(10+i-3,RIGHT,actual[i] == prescribed[i] ? "VERIFIED" : "");
  }

  time(&t);
  strftime(tmp,50,"%F",localtime(&t));
  mvprintw(20,2,"DATE: %s",tmp);
  strftime(tmp,50,"%T",localtime(&t));
  mvprintw(21,2,"TIME: %s",tmp);
  mvprintw(22,2,"OPR ID: 033-%s",getenv("USER"));

  mvprintw(20,CENTER_LEFT-9,"SYSTEM: %s",MODE_TYPES[mode]);
  mvprintw(21,CENTER_LEFT-9,"TREAT: TREAT PAUSE");
  mvprintw(22,CENTER_LEFT-9,"REASON: OPERATOR");

  mvprintw(20,CENTER_RIGHT,"OP.MODE: TREAT\tAUTO");
  mvprintw(21,CENTER_RIGHT+9,"X-RAY\t173777");
  mvprintw(22,CENTER_RIGHT,"COMMAND: ");

  //mvprintw(1,RIGHT,"%d",cloc);
  move(curline[cloc],curcol[cloc]);

  refresh();
}


void getinput(WINDOW *w) {
  int c,origcloc;

  origcloc = cloc;

  halfdelay(5);
  noecho();
  c = getch();
  echo();
  nocbreak();
  
  if (c == KEY_ENTER) {
    if (cloc > 5 && cloc < 12)
      prescribed[cloc-3] = actual[cloc-3]; // copy
    if (cloc < CURMAX-1)
      cloc++;
  } else if (c == KEY_UP) {
    if (cloc > 0)
      cloc--;
  } else if (c == KEY_DOWN) {
    if (cloc < CURMAX-1)
      cloc++;
  } else if (c == ERR) {
    // do nothing
  } else {
    ungetch(c);
    if (cloc == 0) {
      if (scanw("%s",name) != ERR)
	cloc++;  
    } else if (cloc == 1) {
      c = getch();
      if (c == 'X' || c == 'x')
	actualbeam = 1;
      else if (c == 'E' || c == 'e')
	actualbeam = 2;
      else
	actualbeam = 0;
      cloc++;  
    } else if (cloc == 2) {
      if (scanw("%d",&energy) != ERR)
	cloc++;  
    } else if (cloc < 12) {
      if (scanw("%lg",&prescribed[cloc-3]) != ERR)
	cloc++;  
    } else {
      c = getch();
      if (c == 'q' || c == 'Q') done = 1;
      if (c == 'b' || c == 'B') {
	doBeam();
      }
    }
  }
  move(curline[origcloc],curcol[origcloc]);
  clrtoeol();

  computeMode();
}

void computeMode(void) {
  int i;
  time_t t;  

  time(&t);
  if (lastcheck > 0) {
    if (t-lastcheck < 8)
      return; // take 8 sec to notice
  }

  mode = strlen(name) > 0 && beam > 0 && energy > 0;  // initial fields set
  for (i=3; i < 9; i++) {
    mode = mode && actual[i] == prescribed[i];        // params match
  }
  mode = mode && cloc == CURMAX-1;                    // cursor on bottom line
  if (mode) {
    mode = 1;
    lastcheck = t;
  } else {
    mode = 0;
    lastcheck = 0;
  }
  beam = actualbeam;
}

void doBeam(void) {
  WINDOW *w2;
  
  w2 = newwin(3,50,12,15);
  box(w2,0,0);
  if (mode == 0)
    mvwprintw(w2,1,2,"MALFUNCTION 13 (Data entry incomplete)");
  else {
    if (actualbeam == beam)
      mvwprintw(w2,1,2,"TREATED %s SUCCESSFULLY!",name);
    else if (actualbeam == 2)
      mvwprintw(w2,1,2,"MALFUNCTION 54 (%d rads delivered)",rand()%10000+10000);
    else
      mvwprintw(w2,1,2,"MALFUNCTION 26 (%d rads delivered)",rand()%10+10);
  }
  wrefresh(w2);
  cbreak();
  getch();
  delwin(w2);
  touchwin(curscr);
  refresh();
}
