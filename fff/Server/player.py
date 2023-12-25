from pygame import *

from fff.Server.lvl import BlockDie, BlockTeleport, Door

MOVE_SPEED = 3
MOVE_EXTRA_SPEED = 2.5
WIDTH = 38
HEIGHT = 48
JUMP_POWER = 10
JUMP_EXTRA_POWER = 1
GRAVITY = 0.35

left = False
right = False


class Player(sprite.Sprite):
    def __init__(self, x, y):
        sprite.Sprite.__init__(self)
        self.winner = False
        self.xvel = 0
        self.startX = x
        self.startY = y
        self.yvel = 0
        self.onGround = False
        self.rect = Rect(x, y, 38, 48)

    def getX(self):
        return self.rect.x

    def getY(self):
        return self.rect.y

    def getPos(self):
        return str(self.rect.x)+" "+str(self.rect.y)

    def updatePos(self, left, right, up, running, platforms):
        if up:
            if self.onGround:
                self.yvel = -JUMP_POWER
                if running and (left or right):
                    self.yvel -= JUMP_EXTRA_POWER

        if left:
            self.xvel = -MOVE_SPEED
            if running:
                self.xvel -= MOVE_EXTRA_SPEED

        if right:
            self.xvel = MOVE_SPEED
            if running:
                self.xvel += MOVE_EXTRA_SPEED

        if not (left or right):
            self.xvel = 0

        if not self.onGround:
            self.yvel += GRAVITY

        self.onGround = False
        self.rect.y += self.yvel
        self.collide(0, self.yvel, platforms)

        self.rect.x += self.xvel
        self.collide(self.xvel, 0, platforms)

    def collide(self, xvel, yvel, platforms):
        for p in platforms:
            if sprite.collide_rect(self, p):
                if isinstance(p, BlockDie):
                    self.die()
                elif isinstance(p, BlockTeleport):
                    self.teleporting(p.goX, p.goY)
                elif isinstance(p, Door):
                    self.winner = True
                else:
                    if xvel > 0:
                        self.rect.right = p.rect.left

                    if xvel < 0:
                        self.rect.left = p.rect.right

                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0

                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                        self.yvel = 0

    def update(self, inp, platforms):
        Words = inp.split(" ")
        if Words[0] == "False":
            left = False
        else:
            left = True
        if Words[1] == "False":
            right = False
        else:
            right = True
        if Words[2] == "False":
            up = False
        else:
            up = True
        if Words[3] == "False":
            running = False
        else:
            running = True
        self.updatePos(left, right, up, running, platforms)

    def die(self):
        self.teleporting(self.startX, self.startY)

    def teleporting(self, goX, goY):
        self.rect.x = goX
        self.rect.y = goY
