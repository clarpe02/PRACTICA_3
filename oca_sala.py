
from multiprocessing.connection import Listener, Client
from multiprocessing import Process, Manager, Value, Lock
import random
import traceback
import sys

BLUE = (0, 0, 255)
YELLOW = (255,255,0)
GREEN = (0,255,0)

dic_casillas={0:[1,1],1:[2,1],2:[3,1],3:[4,1],4:[5,1],5:[6,1],6:[7,1],7:[8,1],
              8:[9,1],9:[10,1],10:[10,2],11:[10,3],12:[10,4],13:[10,5],14:[10,6],
              15:[10,7],16:[9,7],17:[8,7],18:[7,7],19:[6,7],20:[5,7],21:[4,7],
              22:[3,7],23:[2,7],24:[1,7],25:[1,6],26:[1,5],27:[1,4],28:[1,3],
              29:[1,2],30:[2,2],31:[3,2],32:[4,2],33:[5,2],34:[6,2],35:[7,2],
              36:[8,2],37:[9,2],38:[9,3],39:[9,4],40:[9,5],41:[9,6],42:[8,6],
              43:[7,6],44:[6,6],45:[5,6],46:[4,6],47:[3,6],48:[2,6],49:[2,5],
              50:[2,4],51:[2,3],52:[3,3],53:[4,3],54:[5,3],55:[6,3],56:[7,3],
              57:[8,3],58:[8,4],59:[8,5],60:[7,5],61:[6,5],62:[5,5]}

ocas={}
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
        self.pos=[0,0]
        
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
    def __init__(self, manager):
        self.posiciones=manager.list([0,0,0])
        self.fichas=manager.list([Ficha(GREEN),Ficha(YELLOW),Ficha(BLUE)])
        self.lock=Lock()
        self.running=Value('b',True)
        self.turnos=Value('i',0)

    def get_ficha(self, color):
        if color==GREEN:
            return self.fichas[0]
        elif color==YELLOW:
            return self.fichas[1]
        elif color==BLUE:
            return self.fichas[2]
        else:
            return 'Ese color no existe'

    def get_casillas(self):
        return self.posiciones

    def is_running(self):
        return self.running.value
    
    def stop(self):
        self.running.value=1
        
    def es_turno(self,n_ficha):
        return self.turnos.value==n_ficha
        
    def ejecutar_turno(self,n):
        self.lock.acquire()
        f=self.fichas[n]
        i=random.randint(1,6)
        f.move(i)   
        casilla=self.posiciones[n]
        for i in range(len(ocas)):
            if casilla==ocas[i]:
                casilla=ocas[(i+1)%len(ocas)]
                f.move_hasta(casilla)
                print("De oca a oca y tiro porque me toca")
        if casilla==6:
            f.move_hasta(12)
            print("De puente a puente y tiro porque me lleva la corriente")
        elif casilla==12:
            f.move_hasta(6)
            print("De puente a puente y tiro porque me lleva la corriente")
        elif casilla==26:
            f.move_hasta(53)
            print("De dado a daod y tiro popque me ha tocado")
        elif casilla==53:
            f.move_hasta(26)
            print("De dado a daod y tiro popque me ha tocado")
        elif casilla==42:
            f.move_hasta(30)
            print("Del laberinto al 30")
        elif casilla==58:
            f.move_hasta(0)
            print("Has muerto, vuelves a la casilla de salida")
        elif casilla>62:
            dif=casilla-62
            f.move_hasta(62-dif)
            
        elif casilla==15:
            pos=random.randint(1,6)
            if pos%2==0:
                f.move_hasta(0)
            else:
                f.move_hasta(35)
            print("He caido en el rayo, a veces acelero, a veces me desmayo")
        else:
            self.turnos.value=(self.turnos.value+1)%3
        self.lock.release()
        
    def get_info(self):
        info = {
            'pos_1': self.fichas[0].get_casilla(),
            'pos_2': self.fichas[1].get_casilla(),
            'pos_3': self.fichas[2].get_casilla(),
            'turno': self.turnos.value,
            'running': self.running.value
        }
        return info
    
    def __str__(self):
        return f"verde:{self.fichas[0].get_casilla()}, amarillo:{self.fichas[1].get_casilla()}, azul:{self.fichas[2].get_casilla()}"

def player(n_ficha,conn,game):
    try:
        print(f"Jugador nuevo")
        conn.send((n_ficha,game.get_info()))
        print("recibe")
        print(game.is_running())
        while game.is_running():
            command=""
            print("entra")
            while command != "next":
                print(conn.poll())
                command = conn.recv()#EL PROBLEMA ESTÁ AQUÍ, POR ALGÚN MOTIVO ESTO NO RECIBE NADA
                print("el comando es" +command)
                if command == "up":
                    game.ejecutar_turno(n_ficha)
            conn.send(game.get_info())
    except:
        print("except")
        traceback.print_exc()
        conn.close()
    finally:
        print(f"Madre mía se acabo la partida")
        
def main(ip_address):
    manager = Manager()
    try:
        with Listener((ip_address,6565),
                      authkey=b'secret password') as listener:
            n_fichas = 0
            fichas = [None, None, None]
            game = Game(manager)
            while True:
                print(f"accepting connection {n_fichas}")
                conn = listener.accept()
                fichas[n_fichas] = Process(target=player,
                                            args=(n_fichas, conn, game))
                n_fichas += 1
                if n_fichas==3:
                    fichas[0].start()
                    fichas[1].start()
                    fichas[2].start()
                    n_fichas=0
                    fichas=[None,None,None]
                    game=Game(manager)
    
    except Exception as e:
        traceback.print_exc()
    
    
if __name__=='__main__':
    ip_address = "127.0.0.1"
    if len(sys.argv)>1:
        ip_address = sys.argv[1]

    main(ip_address)
    
    
    
    
        
    
    