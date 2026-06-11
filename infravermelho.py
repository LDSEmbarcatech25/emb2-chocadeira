from machine import Pin

class SensorInfravermelho:
    def __init__(self, pino):
        self.pino = Pin(pino, Pin.IN)

    def status(self):
        # Módulos HW-201 enviam 0 quando detectam obstáculo (tampa fechada)
        # O sistema exige: 1 (ON) = Fechada, 0 (OFF) = Aberta
        if self.pino.value() == 0:
            return 1 # ON - Tampa Fechada
        else:
            return 0 # OFF - Tampa Aberta