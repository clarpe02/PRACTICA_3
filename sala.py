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

ocas=[5,9,14,18,23,27,32,36,41,45,50,54,59]

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
        pos_cas=pos_casilla(self.casilla)
        self.pos=pos_cas
        
    def move_hasta(self,n):
        self.casilla=n
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
        self.bloqueo=manager.list([False,False,False])
        self.turnos_bloqueo=manager.list([0,0,0])
        self.mensaje=""

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
        mensaje=""
        print("el bloqueo es : ")
        print(self.bloqueo[n])
        if self.bloqueo[n]==True:
            self.turnos_bloqueo[n]-=1
            if self.turnos_bloqueo[n]==0:
                self.bloqueo[n]=False
            self.turnos.value=(self.turnos.value+1)%3
        else:
            i=random.randint(1,6)
            self.posiciones[n]=self.posiciones[n]+i  
            casilla=self.posiciones[n]
            print("La casilla es :" +str(casilla))
            oca=False
            puente=False
            dado=False
            while i<len(ocas) and not oca:
                if casilla==ocas[i]:
                    casilla=ocas[(i+1)%len(ocas)]
                    self.posiciones[n]=casilla
                    oca=True
                    mensaje="De oca a oca y tiro porque me toca"
                i+=1
            if casilla==6:
                self.posiciones[n]=12
                puente=True
                mensaje="De puente a puente y tiro porque me lleva la corriente"
            elif casilla==12:
                self.posiciones[n]=6
                puente=True
                mensaje="De puente a puente y tiro porque me lleva la corriente"
            elif casilla==26:
                self.posiciones[n]=53
                dado=True
                mensaje="De dado a dado y tiro porque me ha tocado"
            elif casilla==53:
                self.posiciones[n]=26
                dado=True
                mensaje="De dado a dado y tiro porque me ha tocado"
            elif casilla==42:
                self.posiciones[n]=30
                mensaje="Del laberinto al 30"
            elif casilla==58:
                self.posiciones[n]=0
                mensaje="Has muerto, vuelves a la casilla de salida"           
            elif casilla==15:
                pos=random.randint(1,6)
                if pos%2==0:
                    self.posiciones[n]=0
                else:
                    self.posiciones[n]=35
                mensaje="He caido en el rayo, a veces acelero, a veces me desmayo"
            elif casilla==19:
                self.bloqueo[n]=True
                self.turnos_bloqueo[n]=2
                mensaje="Has caido en la posada, dos turnos sin tirar"
            elif casilla==56:
                self.bloqueo[n]=True
                self.turnos_bloqueo[n]=3
                mensaje="Has caido en la prisión, tres turnos sin tirar"
            print("oca"+str(oca)+"puente"+str(puente)+"dado"+str(dado))
            if not oca and not puente and not dado:
                self.turnos.value=(self.turnos.value+1)%3
        print("TUrno"+str(self.turnos.value))
        self.mensaje=mensaje
        self.lock.release()
        
    def get_info(self):
        info = {
            'pos_1': self.posiciones[0],
            'pos_2': self.posiciones[1],
            'pos_3': self.posiciones[2],
            'turno': self.turnos.value,
            'running': self.running.value,
            'mensaje': self.mensaje
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
                if command == "up" and game.es_turno(n_ficha):
                    game.ejecutar_turno(n_ficha)
                elif command == "up" and not(game.es_turno(n_ficha)):
                    print("No te toca aún, tramposo") 
            gameinfo=game.get_info()
            print(gameinfo)
            conn.send(gameinfo)
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