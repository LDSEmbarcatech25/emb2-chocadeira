from machine import Pin
import time

class ControleRele:
    def __init__(self, pin_rele, nome="RELE"):
        # Lógica original restaurada: ativo em ALTO (1 = Ligado, 0 = Desligado)
        self.pino = Pin(pin_rele, Pin.OUT, value=0)
        self._ligado = False
        self.nome = nome

    def ligar(self):
        self.pino.value(1)
        self._ligado = True
        print("► {} LIGADO".format(self.nome))

    def desligar(self):
        self.pino.value(0)
        self._ligado = False
        print("► {} DESLIGADO".format(self.nome))

    def estado(self):
        return self._ligado

    def atualizar_por_setpoint(self, temperatura, setpoint, tampa_aberta):
        if temperatura is None:
            return

        # Segurança: se a tampa estiver aberta, força o desligamento
        if tampa_aberta:
            if self.estado():
                self.desligar()
            return

        # Controle On/Off pelo Setpoint
        if temperatura < setpoint and not self.estado():
            self.ligar()
        elif temperatura >= setpoint and self.estado():
            self.desligar()


class ControleVentoinha:
    def __init__(self, pin_rele, nome="VENTOINHA", atraso_liga_ms=1000, atraso_desliga_ms=1000):
        # Lógica original restaurada: ativo em ALTO (1 = Ligado, 0 = Desligado)
        self.pino = Pin(pin_rele, Pin.OUT, value=0)
        self._ligada = False
        self.nome = nome
        self.atraso_liga_ms = atraso_liga_ms
        self.atraso_desliga_ms = atraso_desliga_ms
        self.inicio_acima = None
        self.inicio_abaixo = None

    def ligar(self):
        self.pino.value(1)
        self._ligada = True
        self.inicio_acima = None
        self.inicio_abaixo = None
        print("► {} LIGADA".format(self.nome))

    def desligar(self):
        self.pino.value(0)
        self._ligada = False
        self.inicio_acima = None
        self.inicio_abaixo = None
        print("► {} DESLIGADA".format(self.nome))

    def estado(self):
        return self._ligada

    def atualizar_por_setpoint(self, temperatura, setpoint, tampa_aberta):
        if temperatura is None:
            self.inicio_acima = None
            self.inicio_abaixo = None
            return

        agora = time.ticks_ms()

        # Segurança: tampa aberta = ventoinha DESLIGADA
        if tampa_aberta:
            if self._ligada:
                self.desligar()
            self.inicio_acima = None
            self.inicio_abaixo = None
            return

        # Liga 1 grau acima do setpoint
        limite_liga = setpoint + 1.5

        if not self._ligada:
            if temperatura >= limite_liga:
                if self.inicio_acima is None:
                    self.inicio_acima = agora
                elif time.ticks_diff(agora, self.inicio_acima) >= self.atraso_liga_ms:
                    self.ligar()
            else:
                self.inicio_acima = None
        else:
            if temperatura <= setpoint:
                if self.inicio_abaixo is None:
                    self.inicio_abaixo = agora
                elif time.ticks_diff(agora, self.inicio_abaixo) >= self.atraso_desliga_ms:
                    self.desligar()
            else:
                self.inicio_abaixo = None