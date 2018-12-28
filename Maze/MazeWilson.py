# This is a 'square' maze generator using wilson span algorithm
# It will output a list of cells with info of existence of walls around the cell

# print function after shape sign is for debuging

# Since all cell in the maze is connected, we could just break down a rectangle shape
# to several square.

# code with love by ChexterWang

import numpy as np
from numpy.random import random_integers as rand
# ==================================================================================================================
class cell():
    def __init__(self, x, y, w, h):
        self.x, self.y = x, y
        self.wallN = self.wallE = self.wallS = self.wallW = 1
        if x == 0:      self.wallW = 8
        if x == w-1:    self.wallE = 8
        if y == 0:      self.wallS = 8
        if y == h-1:    self.wallN = 8
        self.maze = False
        self.dir = None
    def getCellinfo(self):
        return np.array([(self.x, self.y), [self.wallN, self.wallE, self.wallS, self.wallW], self.dir])
    def setCellinfo(self, N, E, S, W, D):
        self.wallN, self.wallE, self.wallS, self.wallW, self.dir = N, E, S, W, D
    def getWall(self):
        return [self.wallN, self.wallE, self.wallS, self.wallW]
    def sumWall(self):
        sum = 0
        for i in self.getWall():
            if i == 8: sum += 1
            elif i:    sum += 1
        return sum
    def __str__(self):
        print('(%d, %d) %d/%d/%d/%d'%(self.x, self.y, self.wallN, self.wallE, self.wallS, self.wallW))
# ==================================================================================================================
def createGrid(w, h):
    _grid = np.empty((w, h), dtype = object)
    for x, i in enumerate(_grid):
        for y, j in enumerate(i):
            _grid[x, y] = cell(x, y, w, h)
    return _grid
# ==================================================================================================================
def createRemain(w, h):
    _remain = np.empty(w*h, dtype = object)
    cnt = 0
    for i in range(w):
        for j in range(h):
            _remain[cnt], cnt = (i, j), cnt+1
    return _remain
# ==================================================================================================================
def toMaze(_remain, _grid, cor):
    # print('toMaze\t\t', cor)
    for i, j in enumerate(_remain):
        if j == cor:    _remain = np.delete(_remain, i, axis = 0);    break
    _grid[cor].maze = True
    # print('remain\t\t', len(_remain))
    return _remain, _grid
# ==================================================================================================================
def walk(_remain, _grid):
    path = np.empty((0, 3), dtype = object)
    w, h = _grid.shape[1], _grid.shape[0]
    start = _remain[rand(0, len(_remain)-1)]
    path = np.append(path, [_grid[start].getCellinfo()], axis = 0)
    now = start
    # print('start\t\t', path)
    # start walking
    while True:
        erase = 0
        while True:
            dir = rand(1, 4) # 1 = W, 2 = D, 3 = S, 4 = A
            if dir == 1 and now[1] < h-1:   next = (now[0], now[1]+1);  break
            elif dir == 2 and now[0] < w-1: next = (now[0]+1, now[1]);  break
            elif dir == 3 and now[1] > 0:   next = (now[0], now[1]-1);  break
            elif dir == 4 and now[0] > 0:   next = (now[0]-1, now[1]);  break
        # print('direction\t', dir, next)
        nowCellInfo, nextCellInfo = np.array(path[-1]), _grid[next].getCellinfo()
        nowCellInfo[2] = dir
        # complete walk
        if _grid[next].maze == True:
            if dir == 1:    nowCellInfo[1][0] = nextCellInfo[1][2] = 0
            elif dir == 2:  nowCellInfo[1][1] = nextCellInfo[1][3] = 0
            elif dir == 3:  nowCellInfo[1][2] = nextCellInfo[1][0] = 0
            elif dir == 4:  nowCellInfo[1][3] = nextCellInfo[1][1] = 0
            path[-1] = nowCellInfo
            path = np.append(path, [nextCellInfo], axis = 0)
            for i in path:
                _grid[i[0]].setCellinfo(i[1][0], i[1][1], i[1][2], i[1][3], i[2])
                _remain, _grid = toMaze(_remain, _grid, i[0])
# ==================================================================================================================
#           for i in range(w):
#               for j in range(h):
#                   _grid[i, j].__str__()
# ==================================================================================================================
            return _remain, _grid
            break
        # erase the loop
        else:
            for index, i in enumerate(path):
                if i[0] == next:
                    # print('erasing\t\t', i[0])
                    if i[2] == 1:    era = [i[0], [1, i[1][1], i[1][2], i[1][3]], i[2]]
                    elif i[2] == 2:  era = [i[0], [i[1][0], 1, i[1][2], i[1][3]], i[2]]
                    elif i[2] == 3:  era = [i[0], [i[1][0], i[1][1], 1, i[1][3]], i[2]]
                    elif i[2] == 4:  era = [i[0], [i[1][0], i[1][1], i[1][2], 1], i[2]]
                    for j in range(index, len(path)):
                        path = np.delete(path, index, axis = 0)
                    path = np.append(path, [era], axis = 0)
                    # print('erased path\n', path)
                    erase = True
                    break
            # keep walking
            if not erase:
                if dir == 1:    nowCellInfo[1][0] = nextCellInfo[1][2] = 0
                elif dir == 2:  nowCellInfo[1][1] = nextCellInfo[1][3] = 0
                elif dir == 3:  nowCellInfo[1][2] = nextCellInfo[1][0] = 0
                elif dir == 4:  nowCellInfo[1][3] = nextCellInfo[1][1] = 0
                path[len(path)-1] = nowCellInfo
                path = np.append(path, [nextCellInfo], axis = 0)
                # print('not erased\n', path)
            now = next

# ==================================================================================================================
def maze(n=5): # example of create a maze
    w = h = n
    remain, grid = createRemain(w, h), createGrid(w, h)
    remain, grid = toMaze(remain, grid, (rand(0, w-1), rand(0, h-1)))
    while len(remain) > 0:
        remain, grid = walk(remain, grid)
    # for i in range(w):
    #     for j in range(h):
    #         grid[i, j].__str__()
    return grid
