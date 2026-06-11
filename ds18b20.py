import machine
import onewire
import ds18x20
import time

class SensorDS18B20:
    def __init__(self, pino):
        self.pino = machine.Pin(pino)
        self.ds_sensor = ds18x20.DS18X20(onewire.OneWire(self.pino))
        self.roms = []
        self.ultima_leitura = None
        self.tempo_conversao = 0
        self.convertendo = False
        self.iniciar_barramento()

    def iniciar_barramento(self):
        try:
            self.roms = self.ds_sensor.scan()
            if self.roms:
                print("DS18B20 encontrado na caixa!")
            else:
                print("Aviso: Nenhum DS18B20 detectado.")
        except Exception as e:
            print("Erro no barramento 1-Wire:", e)

    def atualizar(self):
        if not self.roms:
            return self.ultima_leitura

        agora = time.ticks_ms()

        if not self.convertendo:
            try:
                self.ds_sensor.convert_temp()
                self.tempo_conversao = agora
                self.convertendo = True
            except Exception as e:
                print("Erro comando DS18B20:", e)
        else:
            # O DS18B20 precisa de até 750ms para finalizar a leitura da temperatura
            if time.ticks_diff(agora, self.tempo_conversao) >= 750:
                try:
                    self.ultima_leitura = round(self.ds_sensor.read_temp(self.roms[0]), 1)
                except Exception as e:
                    print("Erro leitura DS18B20:", e)
                self.convertendo = False

        return self.ultima_leitura