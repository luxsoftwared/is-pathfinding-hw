import math
import os
import random

import pygame

import config

from itertools import permutations 
from queue import PriorityQueue


class BaseSprite(pygame.sprite.Sprite):
    images = dict()

    def __init__(self, x, y, file_name, transparent_color=None, wid=config.SPRITE_SIZE, hei=config.SPRITE_SIZE):
        pygame.sprite.Sprite.__init__(self)
        if file_name in BaseSprite.images:
            self.image = BaseSprite.images[file_name]
        else:
            self.image = pygame.image.load(os.path.join(config.IMG_FOLDER, file_name)).convert()
            self.image = pygame.transform.scale(self.image, (wid, hei))
            BaseSprite.images[file_name] = self.image
        # making the image transparent (if needed)
        if transparent_color:
            self.image.set_colorkey(transparent_color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Surface(BaseSprite):
    def __init__(self):
        super(Surface, self).__init__(0, 0, 'terrain.png', None, config.WIDTH, config.HEIGHT)


class Coin(BaseSprite):
    def __init__(self, x, y, ident):
        self.ident = ident
        super(Coin, self).__init__(x, y, 'coin.png', config.DARK_GREEN)

    def get_ident(self):
        return self.ident

    def position(self):
        return self.rect.x, self.rect.y

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.BLACK)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class CollectedCoin(BaseSprite):
    def __init__(self, coin):
        self.ident = coin.ident
        super(CollectedCoin, self).__init__(coin.rect.x, coin.rect.y, 'collected_coin.png', config.DARK_GREEN)

    def draw(self, screen):
        text = config.COIN_FONT.render(f'{self.ident}', True, config.RED)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)


class Agent(BaseSprite):
    def __init__(self, x, y, file_name):
        super(Agent, self).__init__(x, y, file_name, config.DARK_GREEN)
        self.x = self.rect.x
        self.y = self.rect.y
        self.step = None
        self.travelling = False
        self.destinationX = 0
        self.destinationY = 0

    def set_destination(self, x, y):
        self.destinationX = x
        self.destinationY = y
        self.step = [self.destinationX - self.x, self.destinationY - self.y]
        magnitude = math.sqrt(self.step[0] ** 2 + self.step[1] ** 2)
        self.step[0] /= magnitude
        self.step[1] /= magnitude
        self.step[0] *= config.TRAVEL_SPEED
        self.step[1] *= config.TRAVEL_SPEED
        self.travelling = True

    def move_one_step(self):
        if not self.travelling:
            return
        self.x += self.step[0]
        self.y += self.step[1]
        self.rect.x = self.x
        self.rect.y = self.y
        if abs(self.x - self.destinationX) < abs(self.step[0]) and abs(self.y - self.destinationY) < abs(self.step[1]):
            self.rect.x = self.destinationX
            self.rect.y = self.destinationY
            self.x = self.destinationX
            self.y = self.destinationY
            self.travelling = False

    def is_travelling(self):
        return self.travelling

    def place_to(self, position):
        self.x = self.destinationX = self.rect.x = position[0]
        self.y = self.destinationX = self.rect.y = position[1]

    # coin_distance - cost matrix
    # return value - list of coin identifiers (containing 0 as first and last element, as well)
    def get_agent_path(self, coin_distance):
        pass



class PriorityEntity(object):
    def __str__(self):
        return "(" + str(self.cost) + ", " + str(self.path) + ", " + str(self.unvisited) + ")"

    def __init__(self, cost, path, unvisited):
        self.cost = cost
        self.path = path
        self.unvisited = unvisited

    def __lt__(self, other):
        less = True
        if self.cost < other.cost:
            less = True
        elif self.cost > other.cost:
            less = False
        elif len(self.path) > len(other.path):
            less = True
        elif len(self.path) < len(other.path):
            less = False
        elif self.path[-1] < other.path[-1]:
            less = True
        else:
            less = False
        return less


def calcMSTcost(node, coin_distance):
    #print("Calculating MST for path:" + str(node))
    currCost = 0
    left = set(node.unvisited)
    left.add(0)
    left.add(node.path[-1])
    pq = PriorityQueue()
    pq.put((0,node.path[-1]))
    while not len(left) == 0:
        min = pq.get()
        if not (min[1] in left):
            continue
        currCost = currCost + min[0]
        left.remove(min[1])
        for i in left:
            pq.put( (coin_distance[min[1]][i], i) )
    #print("MST is:" + str(currCost))
    return currCost

class PriorityEntityMicko(object):
    
    def __init__(self, cost, path, unvisited, coin_distance):
        self.cost = cost
        self.path = path
        self.unvisited = unvisited
        self.MSTcost = calcMSTcost(self, coin_distance)
    
    def __str__(self):
        return "(" + str(self.cost) + ", " + str(self.path) + ", " + str(self.unvisited) + ")"

    def __repr__(self):
        return "(" + str(self.cost) + ", " + str(self.path) + ", " + str(self.unvisited) + ")"
        

    def __lt__(self, other):
        less = True
        if self.cost + self.MSTcost < other.cost + other.MSTcost:
            less = True
        elif self.cost + self.MSTcost > other.cost + other.MSTcost:
            less = False
        elif len(self.path) > len(other.path):
            less = True
        elif len(self.path) < len(other.path):
            less = False
        elif self.path[-1] < other.path[-1]:
            less = True
        else:
            less = False
        return less
    
    
class ExampleAgent(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        path = [i for i in range(1, len(coin_distance))]
        random.shuffle(path)
        return [0] + path + [0]

class Aki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        stack = [0]
        unvisited = set(range(1,len(coin_distance)))

        while len(unvisited) > 0:
            curr = stack[-1]
            min = unvisited.pop()
            min_dist = coin_distance[curr][min]
            unvisited.add(min)
            for i in unvisited:
                if coin_distance[curr][i] < min_dist or (coin_distance[curr][i] == min_dist and i < min):
                    min = i
                    min_dist = coin_distance[curr][i]
            stack.append(min)
            unvisited.remove(min)
        stack.append(0)
        return stack

class Jocke(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        allPermutations = list(permutations(range(1,len(coin_distance))))
        min_cost = 0
        path = []
        for perm in allPermutations:
            perm = list(perm)
            cost = 0
            prev = 0
            for curr in perm:
                cost = cost + coin_distance[prev][curr]
                prev = curr;
            cost = cost + coin_distance[prev][0]
            if len(path) == 0 or cost < min_cost:
                min_cost = cost
                path = perm
        return [0] + path + [0];


class Uki(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        cost = 0
        path = [0]
        unvisited = set(range(1,len(coin_distance)))
        paths = PriorityQueue()
        paths.put(PriorityEntity(cost, path, unvisited))
        while not paths.empty():
            exp = paths.get()
            if len(exp.path) == len(coin_distance) + 1:#exit
                path = exp.path
                break 
            if len(exp.unvisited)==0 :
                cost = exp.cost + coin_distance[exp.path[-1]][0]
                path = exp.path + [0]
                unvisited = set()
                paths.put(PriorityEntity(cost, path, unvisited))                
            for coin in exp.unvisited:
                cost = exp.cost + coin_distance[exp.path[-1]][coin]     #coin_distance[last in path][next]
                path = exp.path + [coin]
                unvisited = set(exp.unvisited)
                unvisited.remove(coin)
                paths.put(PriorityEntity(cost, path, unvisited))
        return path

    
class Micko(Agent):
    def __init__(self, x, y, file_name):
        super().__init__(x, y, file_name)

    def get_agent_path(self, coin_distance):
        try:
            cost = 0
            path = [0]
            unvisited = set(range(1,len(coin_distance)))
            paths = PriorityQueue()
            paths.put(PriorityEntityMicko(cost, path, unvisited, coin_distance))
            while not paths.empty():
                #print("PriorityQueue: "+ str(paths.queue))
                exp = paths.get()
                if len(exp.path) == len(coin_distance) + 1:#exit
                    path = exp.path
                    break 
                if len(exp.unvisited)==0 :
                    cost = exp.cost + coin_distance[exp.path[-1]][0]
                    path = exp.path + [0]
                    unvisited = set()
                    paths.put(PriorityEntityMicko(cost, path, unvisited, coin_distance))                    
                for coin in exp.unvisited:
                    cost = exp.cost + coin_distance[exp.path[-1]][coin]     #coin_distance[last in path][next]
                    path = exp.path + [coin]
                    unvisited = set(exp.unvisited)
                    unvisited.remove(coin)
                    paths.put(PriorityEntityMicko(cost, path, unvisited, coin_distance))
            return path
        except Exception as e: print(e)



