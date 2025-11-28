from flask import Flask, render_template
from flask_socketio import SocketIO
import time
import random
from threading import Lock

app = Flask(__name__, template_folder='.') # Busca el HTML en la misma carpeta
socketio = SocketIO(app, cors_allowed_origins="*")

# --- CONFIGURACIÓN ---
N_FILOSOFOS = 5
# Estados: 0 = PENSANDO, 1 = HAMBRIENTO, 2 = COMIENDO
ESTADOS = ['THINKING'] * N_FILOSOFOS
TENEDORES = [True] * N_FILOSOFOS # True = Libre, False = Ocupado
thread = None
thread_lock = Lock()

def simulacion_filosofos():
    """Esta función corre en segundo plano y maneja la lógica pura"""
    while True:
        cambio_hubo = False
        
        for i in range(N_FILOSOFOS):
            izq = i
            der = (i + 1) % N_FILOSOFOS
            
            # LÓGICA DEL FILÓSOFO
            
            # Si está PENSANDO, tiene probabilidad de tener HAMBRE
            if ESTADOS[i] == 'THINKING':
                if random.random() < 0.1: # 10% chance por ciclo
                    ESTADOS[i] = 'HUNGRY'
                    cambio_hubo = True

            # Si está HAMBRIENTO, intenta comer
            elif ESTADOS[i] == 'HUNGRY':
                # Verifica si ambos tenedores están libres
                if TENEDORES[izq] and TENEDORES[der]:
                    TENEDORES[izq] = False
                    TENEDORES[der] = False
                    ESTADOS[i] = 'EATING'
                    # Le asignamos un tiempo de comida (simulado aquí con un contador simple o manejado por el loop)
                    socketio.emit('log', {'msg': f'Filósofo {i} comenzó a comer'})
                    cambio_hubo = True

            # Si está COMIENDO, tiene probabilidad de terminar
            elif ESTADOS[i] == 'EATING':
                if random.random() < 0.05: # 5% chance de terminar por ciclo
                    TENEDORES[izq] = True
                    TENEDORES[der] = True
                    ESTADOS[i] = 'THINKING'
                    socketio.emit('log', {'msg': f'Filósofo {i} terminó de comer'})
                    cambio_hubo = True

        # Si hubo algún cambio, enviamos el estado completo al Frontend
        if cambio_hubo:
            socketio.emit('actualizar_estado', {'estados': ESTADOS})
        
        socketio.sleep(0.5) # Velocidad de la simulación (0.5 segundos por ciclo)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect():
    global thread
    print('Cliente conectado')
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(simulacion_filosofos)

if __name__ == '__main__':
    socketio.run(app, debug=True)