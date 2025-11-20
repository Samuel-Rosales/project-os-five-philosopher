import threading
import time
import random

# Constantes del problema
NUM_FILOSOFOS = 5
TIEMPO_COMER = 2
TIEMPO_PENSAR = 2

# Los palillos son los recursos compartidos, representados por cerrojos (Locks)
# Hay 5 palillos, uno entre cada filósofo.
palillos = [threading.Lock() for n in range(NUM_FILOSOFOS)]

def vida_filosofo(i):
    """
    Simula el ciclo de vida de un filósofo (pensar, intentar comer, comer, soltar).
    :param i: Índice del filósofo (0 a 4).
    """
    # Los palillos se identifican por su índice: i y (i+1) % NUM_FILOSOFOS
    palillo_izq = palillos[i]
    palillo_der = palillos[(i + 1) % NUM_FILOSOFOS]

    # Estrategia para EVITAR INTERBLOQUEO:
    # El filósofo 4 (o cualquier filósofo par) toma el palillo derecho primero.
    # El resto toma el palillo izquierdo primero.
    if i == NUM_FILOSOFOS - 1: # Si es el último filósofo (índice 4)
        primer_palillo = palillo_der
        segundo_palillo = palillo_izq
    else: # El resto de filósofos
        primer_palillo = palillo_izq
        segundo_palillo = palillo_der

    while True:
        # 1. PENSAR
        print(f"Filósofo {i} está PENSANDO.")
        time.sleep(random.uniform(1, TIEMPO_PENSAR))

        # 2. INTENTAR TOMAR PALILLOS Y COMER
        print(f"Filósofo {i} tiene HAMBRE y busca palillos.")

        # Tomar el primer palillo
        primer_palillo.acquire()
        print(f"Filósofo {i} tomó su primer palillo.")

        # Intentar tomar el segundo palillo (Bloquea si está ocupado)
        if segundo_palillo.acquire(timeout=0.5): # Tiempo límite para evitar espera eterna.
            # COMER
            print(f"Filósofo {i} está COMIENDO. 🍝")
            time.sleep(TIEMPO_COMER)

            # 3. SOLTAR PALILLOS
            segundo_palillo.release()
            primer_palillo.release()
            print(f"Filósofo {i} SOLTÓ sus palillos y vuelve a pensar.")
        else:
            # Si no pudo tomar el segundo palillo, suelta el primero y vuelve a pensar.
            primer_palillo.release()
            print(f"Filósofo {i} no pudo comer, soltó el palillo y va a PENSAR un poco más.")

# 4. INICIAR LA CENA
if __name__ == "__main__":
    hilos = [threading.Thread(target=vida_filosofo, args=(i,)) for i in range(NUM_FILOSOFOS)]

    for h in hilos:
        h.start()

    # Mantener el programa principal vivo por un tiempo
    time.sleep(15)
    print("\n--- La simulación terminó después de 15 segundos ---")
    # Nota: Los hilos seguirán corriendo hasta que se detenga el proceso manualmente.