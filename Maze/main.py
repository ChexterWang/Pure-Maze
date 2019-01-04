import time
from numpy.random import random_integers as rand
import numpy as np

#==  import kivy  ==========================================================================================================
import kivy
kivy.require('1.10.1')

from kivy.config import Config
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '500')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.image import Image as img
from kivy.core.window import Window
from kivy.clock import Clock as clk
from kivy.graphics import *
from kivy.graphics import Color as vec3

#==  import maze algorithm  ================================================================================================
import MazeWilson as mz

#==  import os to get path to main.py  =====================================================================================
import os
global path
path = os.path.dirname(os.path.abspath(__file__))

#==  info jizz string  =====================================================================================================
info = '[GAME   ] [Info        ]'
debug = '[GAME   ] [Debug       ]'

#==  the game object  ======================================================================================================
class testGame(Widget):

  #==  init  ===============================================================================================================
    def __init__(self, **kwargs):
        super(testGame, self).__init__(**kwargs)
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
        self.player = [8.5, 8.5]
        self.wall = [0, 0, 0, 0]
        self.diff = 0 # size of the maze
        self.diffMenu = 0 # difficulty in menu; 0 for easy, 1 for hard
        self.game = False # True if the game is started
        self.loading = False # True if start loading
        self.pause = False # True if the game is paused
        self.pauseMenu = 0 # options in pause menu; 0 for resume, 1 for restart, 2 for quit/back to mene
        self.end = False # True if the game is end
        # touch and move state
        self.touch = False
        self.target = [400, 250]
        # items
        self.eatItem = False
        self.gps = False
        self.breaker = False
        self.bgReversed = False
        self.dirReversed = False
        self.glitch = False
        self.range = 1 # 0 = narrow, 1 = normal, 2 = broadened
        self.portal = 0 # 0 = normal, 1 = random, 2 = (0, 0)
        # score
        self.score = 0
        # start update event every 1/60 sec
        self.updateEvent = clk.schedule_interval(self.update, 1/60)

  #==  key input detector  =================================================================================================
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if not self.game: # in menu key detector
            if keycode[1] == 'right':    self.diffMenu += 1
            elif keycode[1] == 'left':   self.diffMenu -= 1
            elif keycode[1] == 'enter':
                if self.diffMenu == 0:   self.diff = 10
                elif self.diffMenu == 1: self.diff = 50
                self.mapLoading()
                self.game = True
            self.diffMenu = self.diffMenu%2
        elif self.game: # in game key detector
            if not self.pause:
                if not self.end:
                    if keycode[1] == 'p': self.pause, self.pauseMenu = not self.pause, 0
                elif self.end:
                    if not self.loading: self.updateEvent.cancel(); self.__init__()
            elif self.pause:
                if keycode[1] == 'p' or (keycode[1] == 'enter' and self.pauseMenu == 0): self.pause = not self.pause
                elif keycode[1] == 'up':    self.pauseMenu -= 1
                elif keycode[1] == 'down':  self.pauseMenu += 1
                elif keycode[1] == 'enter':
                    if self.pauseMenu == 1:   self.player, self.pause = [0.5, 0.5], False
                    elif self.pauseMenu == 2: self.updateEvent.cancel(); self.__init__()
                self.pauseMenu = self.pauseMenu%3

  #==  detect touch input  =================================================================================================
    def on_touch_down(self, touch):
        if not self.game:
            if 125<touch.y<175:
                if 515<touch.x<615:
                    self.diff = 50
                    self.mapLoading()
                    self.game = True
                elif 185<touch.x<285:
                    self.diff = 10
                    self.mapLoading()
                    self.game = True
        elif self.game:
            if not self.pause: self.target, self.touch = [touch.x, touch.y], True
            elif self.pause:
                if 350<touch.x<450:
                    if 350<touch.y<390:   self.pause = not self.pause
                    elif 250<touch.y<290: self.player, self.pause = [0.5, 0.5], False
                    elif 150<touch.y<190: self.updateEvent.cancel(); self.__init__()
        if self.end and not self.loading: self.updateEvent.cancel(); self.__init__()
    def on_touch_move(self, touch):
        if self.game: self.target, self.touch = [touch.x, touch.y], True
    def on_touch_up(self, touch): self.target, self.touch = [400, 250], False
    def on_touch(self):
        speed, eatItem = 3e-4, False
        target = [self.player[0]+speed*(self.target[0]-400), self.player[1]+speed*(self.target[1]-250)]
        if self.dirReversed: target = [self.player[0]-speed*(self.target[0]-400), self.player[1]-speed*(self.target[1]-250)]
        cell = (int(self.player[0]), int(self.player[1]))
        wall = grid[cell].getWall()
        if not self.breaker:
            if wall[0]:
                if target[1] > cell[1]+0.9: target[1] = cell[1]+0.9
            if wall[1]:
                if target[0] > cell[0]+0.9: target[0] = cell[0]+0.9
            if wall[2]:
                if target[1] < cell[1]+0.1: target[1] = cell[1]+0.1
            if wall[3]:
                if target[0] < cell[0]+0.1: target[0] = cell[0]+0.1
        else:
            if target[1] > self.diff-0.1: target[1] = self.diff-0.1
            if target[0] > self.diff-0.1: target[0] = self.diff-0.1
            if target[1] < 0.1: target[1] = 0.1
            if target[0] < 0.1: target[0] = 0.1
        ## == avoid break through; left for be found the bug ===============================================================
        # 1100 0110 0011 1001 1000 0100 0010 0001
        # corner = [(1, 1), (1, 0), (0, 0), (0, 1)]
        # for i in range(4):
        #     if wall[i]+wall[(i+1)%4] == 0:
        #         origin = [cell[0]+corner[i][0], cell[1]+corner[i][1]]
        #         if (target[0]-origin[0])**2+(target[1]-origin[1])**2 < 0.01:
        #             for j in range(100):
        #                 if (self.player[0]+(j/100)*(target[0]-self.player[0])-origin[0])**2 + (self.player[1]+(j/100)*(target[1]-self.player[1])-origin[1])**2 - 0.01 < 1e-4:
        #                     target = [self.player[0]+(j/100)*(target[0]-self.player[0]), self.player[1]+(j/100)*(target[1]-self.player[1])]
        #                     break
        # ==================================================================================================================
        if not self.loading: # check for item eaten
            pos = (int(self.player[0]), int(self.player[1]))
            if pos in item:
                # if the cell player in has item to gather
                if (not grid[pos].getWall()[0] and (target[0]-(cell[0]+0.9))**2+(target[1]-(cell[1]+0.1)) < 0.01)\
                or (not grid[pos].getWall()[1] and (target[0]-(cell[0]+0.1))**2+(target[1]-(cell[1]+0.1)) < 0.01)\
                or (not grid[pos].getWall()[2] and (target[0]-(cell[0]+0.1))**2+(target[1]-(cell[1]+0.9)) < 0.01)\
                or (not grid[pos].getWall()[3] and (target[0]-(cell[0]+0.9))**2+(target[1]-(cell[1]+0.9)) < 0.01):
                    item.remove(pos)
                    self.gps = self.breaker = self.bgReversed = self.dirReversed = self.glitch = False
                    self.range = 1
                    i = rand(0, 84) # determine the possibility of what item player get
                    if i//11 == 0:   self.gps = True
                    elif i//11 == 1: self.bgReversed = True
                    elif i//11 == 2: self.dirReversed = True
                    elif i//11 == 3: self.glitch = True
                    elif i//11 == 4: self.range = 0
                    elif i//11 == 5: self.range = 1
                    elif i//11 == 6: self.range = 2
                    elif i in [77, 78]: self.breaker = True
                    elif i in [79, 80, 81]: target, self.portal = [0.5, 0.5], 1
                    elif i in [82, 83, 84]: target, self.portal = [rand(0, self.diff-1)+0.5, rand(0, self.diff-1)+0.5], 2
                    self.eatItem = True
                    self.score += rand(30, 50)
                    global tE
                    tE = time.time()
        self.player = target

  #==  update the window  ==================================================================================================
    def update(self, dt):
        self.canvas.clear()
        self.clear_widgets()
        if not self.game:
            self.drawMenu()
        elif self.game:
            if self.touch and not self.pause and not self.end: self.on_touch()
            self.drawMap()
            self.drawPlayer()
            if not self.end and self.loading: self.drawLoading()
            if self.touch and not self.pause and not self.end: self.drawDir()
            if self.pause:  self.drawPause()
            if self.end:    self.drawEnd()
            if self.glitch: self.flashing()

  #==  draw menu  ==========================================================================================================
    def drawMenu(self):
        self.canvas.add(vec3(0.18, 0.18, 0.18))
        self.canvas.add(Rectangle(pos = (0, 0), size = (800, 500)))
        self.add_widget(Label(text = 'Pure Maze', pos = (50, 300), size = (350, 100), halign = 'left', valign = 'bottom', font_size = '60sp'))
        self.add_widget(Label(text = 'Easy', pos = (135, 125), size = (200, 50), halign = 'center', valign = 'bottom', font_size = '28sp'))
        self.add_widget(Label(text = 'Hard', pos = (465, 125), size = (200, 50), halign = 'center', valign = 'bottom', font_size = '28sp'))
        self.canvas.add(vec3(1, 1, 1, 0.03))
        j, w, l = 3, 20, 1.5 # j for the gradation gap, w for the width, l for line width
        for i in range(20):
            self.canvas.add(Line(points = (235-w-j*i, 125, 235+w+j*i, 125), width = l))
            self.canvas.add(Line(points = (565-w-j*i, 125, 565+w+j*i, 125), width = l))
            if self.diffMenu == 0:   self.canvas.add(Line(points = (235-w-j*i, 125, 235+w+j*i, 125), width = l))
            elif self.diffMenu == 1: self.canvas.add(Line(points = (565-w-j*i, 125, 565+w+j*i, 125), width = l))

  #==  create map (remove walls gradually)  ================================================================================
    def mapLoading(self):
        self.loading = True
        print('%s Loading'%(info))
        w = h = self.diff
        global remain, grid, tS
        tS = time.time()
        remain, grid = mz.createRemain(w, h), mz.createGrid(w, h)
        remain, grid = mz.toMaze(remain, grid, (rand(0, int(w/2-1)), rand(0, int(h/2-1))))
        def load(dt):
            global remain, grid
            if len(remain) == 0: return False
            remain, grid = mz.walk(remain, grid)
        clk.schedule_interval(load, 1/60)

  #==  draw loading on the game scene  =====================================================================================
    def drawLoading(self):
        if len(remain) == 0:
            print('%s Map loaded; Load time: %.3f sec'%(info, time.time()-tS))
            global item, grid
            item = list()
            for i in range(self.diff):
                for j in range(self.diff):
                    if grid[i, j].sumWall()==3:
                        item.append((i, j))
            if grid[self.diff-1, self.diff-1].sumWall()==3: item.remove((self.diff-1, self.diff-1))
            if grid[0, 0].sumWall()==3: item.remove((0, 0))
            while len(item)>int((self.diff*3/10)**2):
                item.pop(rand(0, len(item)-1))
            global timeStarted
            timeStarted = time.time()
            self.loading = False
        self.canvas.add(vec3(0.38, 0.38, 0.38))
        self.canvas.add(Line(points = (600, 50, 750, 50), width = 2))
        self.canvas.add(vec3(0.11, 1.0, 0.96))
        self.canvas.add(Line(points = (600, 50, 600+150*(1-len(remain)/self.diff**2), 50), width = 2))
        self.add_widget(Label(text = '%d %s'%(100*(1-len(remain)/self.diff**2), '%'), pos = (550, 35), size = (50, 30), halign = 'center', valign = 'bottom', font_size = '16sp'))

  #==  draw direction indicatior  ==========================================================================================
    def drawDir(self):
        r = 4
        self.canvas.add(vec3(255, 255, 255, 0.62))
        self.canvas.add(Ellipse(pos = (self.target[0]-r, self.target[1]-r), size = (2*r, 2*r)))
        if self.bgReversed: self.canvas.add(vec3(0.3, 0.3, 0.3, 0.71))
        self.canvas.add(Line(points = (self.target[0], self.target[1], 400, 250), width = 1))

  #==  draw player  ========================================================================================================
    def drawPlayer(self):
        self.canvas.add(vec3(0.74, 0.91, 0.55)) # the player itself
        self.canvas.add(Line(circle = (400, 250, 5)))
        if self.range == 0: # narraw finder
            for i in range(10):
                self.canvas.add(vec3(0.1, 0.11, 0.13, i/10))
                self.canvas.add(Line(circle = (400, 250, 130+1.5*i), width = 1.5))
                self.canvas.add(vec3(0.1, 0.11, 0.13))
                self.canvas.add(Line(circle = (400, 250, 308.35), width = 163.35))
        elif self.range == 1: # normal finder
            for i in range(10):
                self.canvas.add(vec3(0.1, 0.11, 0.13, i/10))
                self.canvas.add(Line(circle = (400, 250, 160+1.5*i), width = 1.5))
            self.canvas.add(vec3(0.1, 0.11, 0.13))
            self.canvas.add(Line(circle = (400, 250, 323.35), width = 148.35))
        elif self.range == 2: # broadened finder
            for i in range(10):
                self.canvas.add(vec3(0.1, 0.11, 0.13, i/10))
                self.canvas.add(Line(circle = (400, 250, 190+1.5*i), width = 1.5))
            self.canvas.add(vec3(0.1, 0.11, 0.13))
            self.canvas.add(Line(circle = (400, 250, 338.35), width = 133.35))
        if time.time()-tS < 10: # add instruction
            self.add_widget(Label(text = 'Use mouse to drag player around', pos = (32, 30), size = (200, 30), halign = 'left', valign = 'bottom', font_size = '16sp'))
            self.add_widget(Label(text = 'Press P for pause',               pos = (50, 10), size = (50, 30),  halign = 'left', valign = 'bottom', font_size = '16sp'))
        if self.gps: # add position info
            self.add_widget(Label(text = '(%.1f, %.1f)'%(self.player[0], self.player[1]), pos = (400, 220), size = (50, 30),  halign = 'left', valign = 'bottom', font_size = '16sp'))
        if self.eatItem: # the pop up of the name of the item
            if time.time()-tE < 3:
                str1, t = 'Effect', time.time()-tE
                if self.gps:            str = 'GPS on'; str1 = 'Item'
                elif self.breaker:      str = 'INVINCIBLE'
                elif self.bgReversed:   str = 'DEADLY WHITE'
                elif self.dirReversed:  str = 'PUSH'
                elif self.glitch:       str = 'POWER FAILURE'
                elif not self.range:    str = 'NARROW MIND'
                elif self.range == 1 and not self.portal: str = 'NORMALIZATION'
                elif self.range == 2:   str = 'HORIZON BROADENED'
                elif self.portal == 1:  str, str1 = 'WELCOME TO FUTURE', 'Portal'
                elif self.portal == 2:  str, str1 = 'WHERE THE F**K AM I?', 'Portal'
                if t<0.4:       x = -875*(t-0.4)**2
                elif 0.4<t<2.6: x = 0
                elif t>2.6:     x = -875*(t-2.6)**2
                self.canvas.add(vec3(0.0, 0.0, 0.0, 0.8))
                self.canvas.add(Rectangle(pos = (x, 350), size = (250, 100)))
                label = Label(text = '%s'%(str),  pos = (100, 375), text_size = (250, 50), size_hint = (1.0, 1.0), halign = 'left', valign = 'middle', font_size = '20sp')
                label.bind(size = label.setter('text_size'))
                self.add_widget(label)
                label = Label(text = '%s'%(str1), pos = (100, 350), text_size = (250, 50), size_hint = (1.0, 1.0), halign = 'left', valign = 'middle', font_size = '16sp')
                label.bind(size = label.setter('text_size'))
                self.add_widget(label)
            else:
                self.portal = 0
                self.eatItem = self.breaker = False
        global timeStarted
        if not self.loading:
            label = Label(text = 'score: %5d (+%3dx7)'%(self.score, 666-(time.time()-timeStarted)), pos = (650, 425), text_size = (170, 50), size_hint = (1.0, 1.0), halign = 'right', valign = 'middle', font_size = '16sp')
            label.bind(size = label.setter('text_size'))
            self.add_widget(label)

  #==  draw map  ===========================================================================================================
    def drawMap(self):
        width, wall = 50, 1 # cell and wall size
        dim = [(width+wall, wall), (wall, width+wall)]
        c = [] # store cell around player
        p = (int(self.player[0]), int(self.player[1])) # store the cell which the player in
        self.wall = grid[p].getWall()
        if p[0]>2 and p[0]<self.diff-3: # store cells around player in c
            for i in range(p[0]-3, p[0]+4):
                if p[1]>2 and p[1]<self.diff-3:
                    for j in range(p[1]-3, p[1]+4):    c.append((i, j))
                elif p[1]<3:
                    for j in range(0, p[1]+4):         c.append((i, j))
                elif p[1]>self.diff-4:
                    for j in range(p[1]-3, self.diff): c.append((i, j))
        elif p[0]<3:
            for i in range(0, p[0]+4):
                if p[1]>2 and p[1]<self.diff-3:
                    for j in range(p[1]-3, p[1]+4):    c.append((i, j))
                elif p[1]<3:
                    for j in range(0, p[1]+4):         c.append((i, j))
                elif p[1]>self.diff-4:
                    for j in range(p[1]-3, self.diff): c.append((i, j))
        elif p[0]>self.diff-4:
            for i in range(p[0]-3, self.diff):
                if p[1]>2 and p[1]<self.diff-3:
                    for j in range(p[1]-3, p[1]+4):    c.append((i, j))
                elif p[1]<3:
                    for j in range(0, p[1]+4):         c.append((i, j))
                elif p[1]>self.diff-4:
                    for j in range(p[1]-3, self.diff): c.append((i, j))
        if self.bgReversed:
            self.canvas.add(vec3(1.0, 1.0, 1.0))
            self.canvas.add(Rectangle(pos = (0, 0), size = (800, 500)))
        if not self.loading:
            global item
            for i in item:
                if i in c:
                    r = ((i[0]-self.player[0])*width+400, (i[1]-self.player[1])*width+250)
                    if int(time.time()*10)%4 == 0:   self.canvas.add(vec3(1.0, 0.58, 0.58))
                    elif int(time.time()*10)%4 == 1: self.canvas.add(vec3(0.62, 1.0, 0.58))
                    elif int(time.time()*10)%4 == 2: self.canvas.add(vec3(0.58, 0.73, 1.0))
                    elif int(time.time()*10)%4 == 3: self.canvas.add(vec3(1.0, 0.58, 0.96))
                    if not grid[i].getWall()[0]:   self.canvas.add(Line(circle = (r[0]+45, r[1]+5, 5), width = 1))
                    elif not grid[i].getWall()[1]: self.canvas.add(Line(circle = (r[0]+5, r[1]+5, 5), width = 1))
                    elif not grid[i].getWall()[2]: self.canvas.add(Line(circle = (r[0]+5, r[1]+45, 5), width = 1))
                    elif not grid[i].getWall()[3]: self.canvas.add(Line(circle = (r[0]+45, r[1]+45, 5), width = 1))
        for i in c: # draw the wall
            for index, j in enumerate(grid[i].getWall()):
                if j:
                    r = ((i[0]-self.player[0])*width+400, (i[1]-self.player[1])*width+250)
                    self.canvas.add(vec3(0.71, 0.62, 0.82))
                    if self.loading:
                        if int(time.time())%3 == 0: self.canvas.add(vec3(0.31, 0.96, 0.71))
                        if int(time.time())%3 == 1: self.canvas.add(vec3(0.87, 0.63, 0.99))
                        if int(time.time())%3 == 2: self.canvas.add(vec3(0.51, 0.66, 0.98))
                    if j == 8:  self.canvas.add(vec3(1.0, 0.39, 0.39))
                    if index == 0:   self.canvas.add(Rectangle(pos = (r[0], r[1]+width),      size = dim[index%2]))
                    elif index == 1: self.canvas.add(Rectangle(pos = (r[0]+width, r[1]-wall), size = dim[index%2]))
                    elif index == 2: self.canvas.add(Rectangle(pos = (r[0]-wall, r[1]-wall),  size = dim[index%2]))
                    elif index == 3: self.canvas.add(Rectangle(pos = (r[0]-wall, r[1]),       size = dim[index%2]))
        if (self.diff-1, self.diff-1) in c:
            if int(time.time())%2 == 0: self.canvas.add(vec3(1.0, 0.25, 0.11))
            if int(time.time())%2 == 1: self.canvas.add(vec3(0.11, 0.91, 1.0))
            self.canvas.add(Rectangle(pos = ((self.diff-1-self.player[0])*width+400+5, (self.diff-1-self.player[1])*width+250+5), size = (width-10, width-10)))
        if self.player[0] > self.diff-1 and self.player[1] > self.diff-1: self.end = self.loading = True

  #==  draw pause  =========================================================================================================
    def drawPause(self):
        self.canvas.add(vec3(0, 0, 0, 0.9))
        self.canvas.add(Rectangle(pos = (0, 0), size = (800, 500)))
        self.canvas.add(vec3(1, 1, 1, 0.03))
        j, w, h, l = 3, 100, 100, 1.5 # j for the gradation gap, w for the width, h for the gap in y axis, l for line width
        for i in range(20):
            self.canvas.add(Line(points = (400-w-j*i, 250+h, 400+w+j*i, 250+h), width = l))
            self.canvas.add(Line(points = (400-w-j*i, 250,   400+w+j*i, 250  ), width = l))
            self.canvas.add(Line(points = (400-w-j*i, 250-h, 400+w+j*i, 250-h), width = l))
            if self.pauseMenu == 0:     self.canvas.add(Line(points = (400-w-j*i, 250+h, 400+w+j*i, 250+h), width = l))
            elif self.pauseMenu == 1:   self.canvas.add(Line(points = (400-w-j*i, 250,   400+w+j*i, 250  ), width = l))
            elif self.pauseMenu == 2:   self.canvas.add(Line(points = (400-w-j*i, 250-h, 400+w+j*i, 250-h), width = l))
        self.add_widget(Label(text = '[color=babbbb]Resume[/color]',  pos = (300, 250+h), size = (200, 45), halign = 'center', valign = 'bottom', font_size = '28sp', markup = True))
        self.add_widget(Label(text = '[color=babbbb]Restart[/color]', pos = (300, 250),   size = (200, 45), halign = 'center', valign = 'bottom', font_size = '28sp', markup = True))
        self.add_widget(Label(text = '[color=babbbb]Quit[/color]',    pos = (300, 250-h), size = (200, 45), halign = 'center', valign = 'bottom', font_size = '28sp', markup = True))

  #==  draw end  =========================================================================================================== ---------------------------------
    global cnt, frameCnt
    cnt, frameCnt = 0, 0
    def drawEnd(self):
        global cnt
        if cnt < 1:
            self.canvas.add(vec3(0.0, 0.0, 0.0, cnt))
            self.canvas.add(Rectangle(pos = (0, 0), size = (800, 500)))
            cnt+=0.007
        else:
            self.gps = self.breaker = self.bgReversed = self.dirReversed = self.glitch = False
            self.range = 1
            self.canvas.add(vec3(0.0, 0.0, 0.0, 1))
            self.canvas.add(Rectangle(pos = (0, 0), size = (800, 500)))
            self.add_widget(Label(text = '[color=babbbb]Any Key[/color]', pos = (252, 325), size = (200, 45), halign = 'center', valign = 'bottom', font_size = '15sp', markup = True))
            self.add_widget(Label(text = '[color=babbbb]Press \u5144\u8cb4 to Continue[/color]', pos = (300, 300), size = (200, 45), halign = 'center', valign = 'bottom', font_size = '30sp', markup = True, font_name = '%s/font/Microsoft JhengHei Bold/Microsoft JhengHei Bold.ttf'%(path)))
            global frameCnt
            self.add_widget(img(source = '%s/img/anikiImg_split/%d.gif'%(path, int(frameCnt)%19), pos = (325, 130), size = (150, 150)))
            frameCnt+=0.25
            def flipLoading(dt): self.loading = False
            clk.schedule_once(flipLoading, 0.5)

  #==  draw flashing  ====================================================================================================== ---------------------------------
    def flashing(self): # create uncomfortable flashing
        if int(rand(0, 100))%3 == 0:
            self.canvas.add(vec3(0.0, 0.0, 0.0, 0.6))
            self.canvas.add(Rectangle(pos = (0, 0), size = (800, 500)))

#==  the app object  =======================================================================================================
class testApp(App):
    def build(self):
        game = testGame()
        print('%s Started'%(info))
        return game

#==  run app  ==============================================================================================================
if __name__ == '__main__':
    testApp().run()
