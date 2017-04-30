#!/usr/bin/python
import pygame,random,math
from pygame.locals import *
from math import fabs
from random import randint
from PIL import Image, ImageFilter
import ImageEnhance
from copy import copy
from json import dumps

class SelectionRect:
    """utility class for using selection rectangles"""
    def __init__(self,screen,start,col=(0,0,0)):
        """
        Constructor.
        Pass starting point of selection rectangle in 'start'
        and color value in which the selection rectangle shall be drawn
        in 'col'
        """
        self.start         = start
        self.col           = col
        self.oldrect       = start[0],start[1],1,1
        tmp                = screen.get_at((start[0],start[1]))[:3]
        self.screen_backup = [[tmp],[tmp],[tmp],[tmp]]
        
    def updateRect(self,now):
        """
        This returns a rectstyle tuple describing the selection rectangle
        between the starting point
        (passed to __init__) and the 'now' edge and
        updates the internal rectangle information for correct drawing.
        """
        x,y = self.start
        mx,my = now
        if mx < x:
            if my < y:
                self.rect = mx,my,x-mx,y-my
            else:
                self.rect = mx,y,x-mx,my-y
        elif my < y:
            self.rect = x,my,mx-x,y-my
        else:
            self.rect = x,y,mx-x,my-y
        return self.rect

    def draw(self,screen):
        """
        This hides the old selection rectangle and draws the current one
        """
        surf = pygame.surfarray.pixels3d(screen)
        r    = self.rect
        # hide selection rectangle
        self.hide(screen)
        
        # update background information
        self.screen_backup[0] = copy(surf[r[0]:r[0]+r[2],r[1]])
        self.screen_backup[1] = copy(surf[r[0]:r[0]+r[2],r[1]+r[3]-1])
        self.screen_backup[2] = copy(surf[r[0],r[1]:r[1]+r[3]])
        self.screen_backup[3] = copy(surf[r[0]+r[2]-1,r[1]:r[1]+r[3]])

        # draw selection rectangle:
        surf[r[0]:r[0]+r[2],r[1]]        = self.col
        surf[r[0]:r[0]+r[2],r[1]+r[3]-1] = self.col
        surf[r[0],r[1]:r[1]+r[3]]        = self.col
        surf[r[0]+r[2]-1,r[1]:r[1]+r[3]] = self.col

        self.oldrect = r
        
        pygame.display.update(r)

    def hide(self,screen):
        """ hide(self,screen)
        This hides the selection rectangle using the stored background
        information. You usually call this after you're finished with the
        selection to hide the last rectangle.
        """
        surf = pygame.surfarray.pixels3d(screen)
        x,y,x2,y2 = self.oldrect[0],self.oldrect[1],\
                    self.oldrect[0]+self.oldrect[2],\
                    self.oldrect[1]+self.oldrect[3]
        surf[x:x2,y   ] = self.screen_backup[0]
        surf[x:x2,y2-1] = self.screen_backup[1]
        surf[x,   y:y2] = self.screen_backup[2]
        surf[x2-1,y:y2] = self.screen_backup[3]
        pygame.display.update(self.oldrect)

def save_embed_image_params(state, out):
    result = {"base": state.base}
    ratioX = float(state.base_size[0]) / state.screen_size[0]
    ratioY = float(state.base_size[1]) / state.screen_size[1]
    result["x"] = round(state.final_rect[0]*ratioX)
    result["mx"] = round(state.final_rect[2]*ratioX)
    result["y"] = round(state.final_rect[1]*ratioY)
    result["my"] = round(state.final_rect[3]*ratioY)
    print "Saving:", result
    with open(out, 'w') as f:
        f.write(dumps(result))
    

def process_events(state):
    for e in pygame.event.get():
        if e.type == QUIT:
            pass
        elif e.type == MOUSEBUTTONDOWN and e.button == 1:
            if not state.selection:
                # begin with selection as
                # the user pressed down the left
                # mouse button
                state.selection = True
                state.rect = SelectionRect(state.screen,e.pos)
        elif e.type == MOUSEMOTION:
            if state.selection:
                # update the selection
                # rectangle while the mouse is moving
                state.rect.updateRect(e.pos)
                state.rect.draw(state.screen)
        elif e.type == MOUSEBUTTONUP and e.button == 1:
            if state.selection:
                state.selection = False
                rect = state.rect.updateRect(e.pos)
                state.rect.hide(state.screen)
                print "Final selection rectangle:",rect
                pygame.draw.rect(state.screen, (233, 200, 100), rect)
                del state.rect
                state.final_rect = rect
        elif e.type == pygame.KEYDOWN:
            if e.key == pygame.K_s:    
                print state.__dict__
                save_embed_image_params(state, "output.txt")

class State(object):
    selection = False
    screen = None
    base = None
    screen_size = None

def main():
    pygame.init()
    state = State()
    screen_width, screen_height = (1024, 600)
    size = (screen_width,screen_height)
    pygame.display.set_caption("Insert Pic")
    surface = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    path = "blank_billboard.jpg"
    base = pygame.image.load(path)
    state.base_size = base.get_size()
    base = pygame.transform.scale(base, size)    
    surface.blit(base, (0,0))    
    state.screen = surface    
    state.screen_size = size
    state.base = path
    
    while(True):
        clock.tick(60)
        process_events(state)
        pygame.display.flip()


if __name__ == '__main__':
    main()
