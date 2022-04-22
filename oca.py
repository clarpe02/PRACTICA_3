import pygame
import os
import time
from multiprocessing.connection import Listener, Client
from multiprocessing import Process, Manager, Value, Lock
import sys
import traceback

#Definimos colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)

#carpetas con imágenes
"""
carpetaDelJuego = os.path.dirname(__file__)
carpetaDeImagenes = os.path.join(carpetaDelJuego,"img")
"""

WIDTH = 1000
HEIGHT = 700
FPS =  1 #frames per second

dic_casillas={0:[1,1],1:[2,1],2:[3,1],3:[4,1],4:[5,1],5:[6,1],6:[7,1],7:[8,1],
              8:[9,1],9:[10,1],10:[10,2],11:[10,3],12:[10,4],13:[10,5],14:[10,6],
              15:[10,7],16:[9,7],17:[8,7],18:[7,7],19:[6,7],20:[5,7],21:[4,7],
              22:[3,7],23:[2,7],24:[1,7],25:[1,6],26:[1,5],27:[1,4],28:[1,3],
              29:[1,2],30:[2,2],31:[3,2],32:[4,2],33:[5,2],34:[6,2],35:[7,2],
              36:[8,2],37:[9,2],38:[9,3],39:[9,4],40:[9,5],41:[9,6],42:[8,6],
              43:[7,6],44:[6,6],45:[5,6],46:[4,6],47:[3,6],48:[2,6],49:[2,5],
              50:[2,4],51:[2,3],52:[3,3],53:[4,3],54:[5,3],55:[6,3],56:[7,3],
              57:[8,3],58:[8,4],59:[8,5],60:[7,5],61:[6,5],62:[5,5]}

def pos_casilla(n):
    pos_cas=-1
    for k in dic_casillas:
        if n==k:
            pos_cas=dic_casillas[k]
    return pos_cas

class Ficha():
    def __init__(self,color):
        self.color=color
        self.casilla=0
        self.pos=[1,1]
        
    def get_color(self):
        return self.color
        
    def get_pos(self):
        return self.pos
    
    def get_casilla(self):
        return self.casilla
    
    def move(self,n):
        self.casilla+=n
        pos_cas=pos_casilla(n)
        self.pos=pos_cas
        
    def __str__(self):
        return f"La ficha {self.color} está en la posición {self.casilla}"
    
class Game():
    def __init__(self):
        self.players=[Ficha(i) for i in range(3)]
        self.turno=0
        self.running=True
        self.lock=Lock()
    
    def get_turno(self):
        return self.turno
    
    def stop(self):
        self.running=False
    
    def is_running(self):
        return self.running
    
    def set_pos_player(self,n_ficha,pos):
        self.players[n_ficha].casilla=pos
    
    def set_turno(self,turno):
        self.turno=turno
    
    def update(self,gameinfo):
        self.set_pos_player(0,gameinfo['pos_1'])
        self.set_pos_player(1,gameinfo['pos_2'])
        self.set_pos_player(2,gameinfo['pos_3'])
        self.set_turno(gameinfo['turno'])
        self.running=gameinfo['running']
        
class Player(pygame.sprite.Sprite):
    def __init__(self,ficha):
        pygame.sprite.Sprite.__init__(self)
        self.ficha = ficha
        self.image = pygame.Surface((50,50)) #Tamaño jugador(ficha rectangular)
        self.image.fill(self.ficha.get_color()) #La ficha será del color elegido
        self.rect = self.image.get_rect() #Rectángulo de posición
        self.rect.center = (0,0) #Queremos que las fichas se inicien en la primera casilla
        
        
    def update(self):
        pos = self.ficha.get_pos()
        self.rect.center = (pos[0]*100/2,pos[1]*100/2)


class Display():
     def __init__(self, player):
         self.player = player
         self.all_sprites = pygame.sprite.Group()
         self.all_sprites.add(player)   
         self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
         self.clock =  pygame.time.Clock()  #FPS
         self.background = pygame.image.load('oca.png')
         pygame.init()
         pygame.display.set_caption("Bienvenido a la oca")
    
    
     def refresh(self):
         self.all_sprites.update()
         self.screen.blit(self.background, (0, 0))
         self.all_sprites.draw(self.screen)
         pygame.display.flip()

     def tick(self):
         self.clock.tick(FPS)
     
     def analyse_events(self,n_ficha):
         events=["up"]
         for event in pygame.event.get():
             if event.type == pygame.KEYDOWN:
                 if event.key == pygame.K_ESCAPE:
                     events.append("quit")
                 elif event.type==pygame.K_UP:
                     events.append("up")
             elif event.type == pygame.QUIT:
                 events.append("quit")
         return events
 
     def quit():
         pygame.quit()
        

def main(ip_address,player):
    try:
        with Client((ip_address, 6000), authkey=b'secret password') as conn:
            game = Game()
            n_ficha,gameinfo = conn.recv()
            print(f"I am playing {n_ficha}")
            game.update(gameinfo)#ahora mismo no funciona porque conn.recv no manda nada eso lo tenemos que arreglar en la sala
            display = Display(player)
            while game.is_running():
                events=display.analyse_events(n_ficha)
                for event in events:
                    conn.send(event)
                    if event.type == pygame.QUIT: #cerrar ventana de juego
                        game.stop()
                conn.send("next")
                gameinfo = conn.recv()
                game.update(gameinfo)
                display.refresh()
                display.tick()
    except:
        traceback.print_exc()
    finally:
        pygame.quit()
"""
def main(ficha,player):
    try:
        game=Game()
        display = Display(player)
        while game.is_running():
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #cerrar ventana de juego
                    running = False
            display.refresh()
            display.tick()
    finally:
        pygame.quit()
        

ficha = Ficha(RED)
player = Player(ficha)
"""
if __name__=="__main__":
    ip_address = "127.0.0.1"
    player=Player(Ficha(RED))
    if len(sys.argv)>1:
        ip_address = sys.argv[1]
    main(ip_address,player)
