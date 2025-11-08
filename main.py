#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Stop, Color
from pybricks.tools import wait
import time

# Create your objects here

# Initialize the EV3 Brick.
ev3 = EV3Brick()

# Motores
left_motor = Motor(Port.A)   # Roda esquerda
claw_open_close = Motor(Port.B)  # Garra abrir/fechar
claw_up_down = Motor(Port.C)     # Garra sobe/desce
right_motor = Motor(Port.D)  # Roda direita

# Sensores
wall_sensor = ColorSensor(Port.S2)       # Sensor de parede (preto/branco) e objeto (vermelho) # Sensor de distancia/objeto

# Funções de movimento

# Fator de correção para calibrar diferenças entre os motores
# Se o robô desvia para a esquerda, reduzir este valor (ex: 0.95)
# Se o robô desvia para a direita, aumentar este valor (ex: 1.05)
# Valor 1.0 = sem correção
MOTOR_CORRECTION_FACTOR = 0.95  # Reduz 5% do motor direito (ajustar conforme necessário)

def mover(speed: int):
    """Move o robô para frente ou para trás."""
    # Invertido o sinal porque os motores estavam indo para trás
    # Aplica fator de correção no motor direito para compensar diferenças
    left_motor.run(-speed)
    right_motor.run(int(-speed * MOTOR_CORRECTION_FACTOR))


def parar():
    """Para o robô rapidamente."""
    left_motor.brake()
    right_motor.brake()


def girar(angle_deg: int, speed: int = 300):
    """Gira o robô em torno do próprio eixo. Ângulo positivo gira para a direita."""
    # Ajuste simplificado: 1 grau de giro ≈ 4.5 deg de rotação da roda (exemplo).
    wheel_turn_angle = angle_deg * -4.5
    left_motor.run_angle(speed, wheel_turn_angle, then=Stop.HOLD, wait=False)
    right_motor.run_angle(speed, -wheel_turn_angle, then=Stop.HOLD, wait=True)

# ---------------- Funções da Garra ----------------

# Valores de referência 
CLAW_OPEN_ANGLE = 320    # Aumentado para abrir mais a garra
CLAW_CLOSE_ANGLE = -700  # Aumentado para fechar com mais força
ARM_DOWN_ANGLE = -90     # Ângulo para baixar a garra normalmente
ARM_DOWN_FINAL_ANGLE = -180  # Dobro do ângulo para baixar completamente no final
ARM_UP_ANGLE = 950       # Aumentado para levantar mais alto antes de soltar
ARM_SPEED = 200
ARM_LIFT_SPEED = 150  # Velocidade reduzida para levantar (evita força excessiva)
CLAW_CLOSE_SPEED = 500  # Velocidade maior para fechar com mais força          


def abrir_garra():
    """Abre a garra até o ângulo definido."""
    claw_open_close.run_angle(ARM_SPEED, CLAW_OPEN_ANGLE, then=Stop.HOLD, wait=True)


def fechar_garra():
    """Fecha a garra com mais força."""
    # Usa velocidade maior para fechar com mais força
    claw_open_close.run_angle(CLAW_CLOSE_SPEED, CLAW_CLOSE_ANGLE, then=Stop.HOLD, wait=True)


def baixar_garra():
    """Baixa a garra para pegar o objeto."""
    claw_up_down.run_angle(ARM_SPEED, ARM_DOWN_ANGLE, then=Stop.HOLD, wait=True)


def baixar_garra_final():
    """Baixa a garra completamente no final (dobro do ângulo normal)."""
    claw_up_down.run_angle(ARM_SPEED, ARM_DOWN_FINAL_ANGLE, then=Stop.HOLD, wait=True)


def levantar_garra():
    """Levanta a garra com o objeto."""
    # Usa run() ao invés de run_angle para evitar travamento físico
    # Roda por um tempo limitado ao invés de tentar completar um ângulo fixo
    # Isso evita que o motor trave tentando girar além do limite físico
    claw_up_down.run(ARM_LIFT_SPEED)  # Inicia movimento
    wait(4000)  # Aguarda 4 segundos (ajuste conforme necessário)
    claw_up_down.stop(Stop.HOLD)  # Para e MANTÉM a posição (evita que a garra caia)
    wait(200)  # Pequeno delay para estabilizar

# ---------------- Sensores e Navegação ----------------

# Limiares (ajustar conforme testes)
DISTANCE_THRESHOLD_MM = 80   # Distância para considerar "objeto detectado" (mm)
SEARCH_TIMEOUT_MS = 30000    # Tempo máximo de busca (ms)


def parede_a_frente() -> bool:
    """Retorna True se o ColorSensor detectar branco (parede) a frente."""
    try:
        cor = wall_sensor.color()
        # Desvia apenas de paredes brancas
        return cor == Color.WHITE
    except:
        return False


def objeto_vermelho_detectado() -> bool:
    """Retorna True se o ColorSensor detectar vermelho (objeto a coletar)."""
    try:
        cor = wall_sensor.color()
        return cor == Color.RED
    except:
        return False


def objeto_vermelho_proximo() -> bool:
    """Detecta objeto vermelho de mais longe usando reflexão e ambiente."""
    try:
        reflexao = wall_sensor.reflection()
        ambiente = wall_sensor.ambient()
        cor = wall_sensor.color()
        
        # Primeiro: verifica se detectou cor vermelha diretamente (mais confiável)
        if cor == Color.RED:
            return True
        
        # Segundo: para objetos distantes, usa combinação de reflexão e ambiente
        # Objetos vermelhos refletem mais luz ambiente que fundos escuros
        # Quando está longe, a reflexão pode ser baixa, mas o ambiente ainda detecta
        if ambiente > 20:  # Ambiente claro indica possível objeto refletindo luz
            # Se há reflexão moderada OU ambiente bem claro, pode ser objeto
            if reflexao > 30 or ambiente > 12:
                return True
        
        # Terceiro: verifica reflexão alta (objeto próximo)
        if reflexao > 30:
            return True
            
        return False
    except:
        return False


def manobra_evasiva():
    """Executa meia-volta para evitar colisao com a parede branca."""
    parar()
    ev3.speaker.beep(frequency=300, duration=100)
    girar(180)  # TODO: ajustar fator se nao girar exatamente 180 graus


def buscar_e_coletar():
    """Busca o objeto vermelho e coleta com a garra. Retorna True se encontrou."""
    # Compatibilidade: usa ticks_ms no MicroPython, time.time no Python padrão
    if hasattr(time, 'ticks_ms'):
        start_time = time.ticks_ms()
        def get_elapsed():
            return time.ticks_diff(time.ticks_ms(), start_time)
    else:
        start_time = int(time.time() * 1000)
        def get_elapsed():
            return int(time.time() * 1000) - start_time

    while get_elapsed() < SEARCH_TIMEOUT_MS:
        # 1. Verifica parede (branca - desvia)
        if parede_a_frente():
            manobra_evasiva()
            continue
        
        # 2. Verifica se detectou objeto vermelho (de longe ou] perto)
        if objeto_vermelho_proximo() or objeto_vermelho_detectado():
            parar()
            wait(150)  # Reduzido para reagir mais rápido
            
            # Confirma que ainda está vendo vermelho
            if objeto_vermelho_detectado() or objeto_vermelho_proximo():
                # 1. ABRE A GARRA primeiro
                #abrir_garra()
                wait(400)  # Aguarda garra abrir completamente
                
                # 2. Avança um pouco para frente para pegar o objeto
                # Avança menos tempo já que detectou mais cedo
                mover(200)  # Velocidade moderada
                wait(300)  # Reduzido de 400ms para 300ms (detectou mais cedo)
                parar()
                wait(150)  # Reduzido de 200ms
                
                # 3. FECHA A GARRA para pegar o objeto
                fechar_garra()
                wait(400)  # Aguarda garra fechar completamente
                
                # 4. LEVANTA A GARRA até a 
                # (armazenar)
                levantar_garra()
                wait(500)  # Aguarda estabilizar após levantar
                
                # 5. ABRE A GARRA para soltar o objeto
                abrir_garra()
                wait(200)  # Aguarda garra abrir completamente para soltar
                
                # 6. BAIXA A GARRA completamente para voltar à posição inicial
                baixar_garra_final()  # Usa o dobro do ângulo para baixar mais
                wait(400)  # Aguarda garra baixar completamente
                
                ev3.speaker.beep(frequency=1000, duration=300)
                return True

        # 3. Avança buscando objeto vermelho
        mover(400)  # TODO: ajustar velocidade
        wait(30)  # Delay reduzido para detectar mais rápido

    return False

# ---------------- Programa Principal ----------------

if __name__ == "__main__":
    ev3.speaker.beep()

    encontrado = buscar_e_coletar()

    if not encontrado:
        ev3.screen.clear()
        ev3.screen.print("Falha em encontrar objeto")
        ev3.speaker.beep(frequency=200, duration=500)   