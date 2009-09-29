import math
import pygame
import pickle

def load(filename, pos, angle, scale):
    f = open(filename, "rb")
    points = pickle.load(f)
    f.close()
    return VectorImage(points, pos, angle, scale)

class VectorImage(object):
    def __init__(self, points, pos, angle, scale):
        self._points = points
        self._draw_points = []
        self._scale = scale
        self._angle = angle
        self._pos = pos
        self._explo = 0
        bx = 0
        by = 0
        sx = 0
        sy = 0
        self.brightness = 2
        for pnts in self._points:
            for p in pnts:
                px = p[0]
                py = p[1]
                if px >= bx:
                    bx = px
                if px <= sx:
                    sx = px 
                if py >= by:
                    by = py
                if py <= sy:
                    sy = py
        self.bx = bx
        self.by = by
        self.sx = sx
        self.sy = sy
        self.width = (self.bx - self.sx)*self._scale
        self.height = (self.by - self.sy)*self._scale
    def update_points(self):
        self.width = (self.bx - self.sx)*self._scale
        self.height = (self.by - self.sy)*self._scale
        x = self.sx + self.width / 2
        y = self.sy + self.height / 2
        self._draw_points = []
        for pnts in self._points:
            new = []
            for p in pnts:
                if self._explo == 0:
                    p0 = p[0]
                    p1 = p[1]
                else:
                    p0 = self.warp(p[0], x, (pnts[0][1]-y)/10*self._explo) + (p[1] - y)/10
                    p1 = self.warp(p[1], y, (pnts[0][0]-x)/10*self._explo) + (p[0] - x)/10
                newX = int(p0*math.cos(math.radians(-self._angle))*self._scale - p1*math.sin(math.radians(-self._angle))*self._scale + self._pos[0])
                newY = int(p0*math.sin(math.radians(-self._angle))*self._scale + p1*math.cos(math.radians(-self._angle))*self._scale + self._pos[1])
                new.append((newX,newY))
            self._draw_points.append(new)
    def draw(self, surface, color=(255, 255, 255), closed_point=True, max=None):
        self.update_points()
        if max is not None and max < 0: max=0
        for pnts in self._draw_points[:max]:
            if pnts:
                try:
                    for i in range(self.brightness):
                        pygame.draw.aalines(surface, color, 0, pnts)
                except:
                    pass
    def scale(self, scale):
        self._scale = scale
    def rotate(self, angle):
        self._angle = angle
    def position(self, pos):
        self._pos = list(pos)
    def points(self):
        return self._draw_points
    def flip(self, flip_x, flip_y):
        new = []
        for pnts in self._points:
            list = []
            for p in pnts:
                x = p[0]
                y = p[1]
                if flip_x:
                    x = -x
                if flip_y:
                    y = -y
                list.append((x, y))
            new.append(list)
        self._points = new
        return self._points
    def warp(self, old, center, amount):
        try:
            return old + math.log((old - center)%5+amount*(old - center))**2
        except ValueError:
            return old
    def explode(self, index):
        self._explo = index
