import time

HDC1080_ADDR = 0x40
REG_TEMPERATURA = 0x00
REG_UMIDADE = 0x01
REG_CONFIG = 0x02


class HDC1080:
    def __init__(self, i2c, endereco=HDC1080_ADDR):
        self.i2c = i2c
        self.endereco = endereco
        self._configurar()

    def _configurar(self):
        try:
            self.i2c.writeto(self.endereco, bytes([REG_CONFIG, 0x00, 0x00]))
            time.sleep_ms(15)
        except Exception as e:
            print("Erro ao configurar HDC1080:", e)

    def ler_temperatura(self):
        try:
            self.i2c.writeto(self.endereco, bytes([REG_TEMPERATURA]))
            time.sleep_ms(15)
            dados = self.i2c.readfrom(self.endereco, 2)
            raw = (dados[0] << 8) | dados[1]
            temperatura = (raw / 65536.0) * 165.0 - 40.0
            return round(temperatura, 1)
        except Exception as e:
            print("Erro ao ler temperatura:", e)
            return None

    def ler_umidade(self):
        try:
            self.i2c.writeto(self.endereco, bytes([REG_UMIDADE]))
            time.sleep_ms(15)
            dados = self.i2c.readfrom(self.endereco, 2)
            raw = (dados[0] << 8) | dados[1]
            umidade = (raw / 65536.0) * 100.0
            return round(umidade, 1)
        except Exception as e:
            print("Erro ao ler umidade:", e)
            return None
