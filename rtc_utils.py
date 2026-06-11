from machine import RTC
import urequests
from config import TIME_API_URL


class RelogioRTC:
    def __init__(self):
        self.rtc = RTC()

    def ajustar(self, ano, mes, dia, hora, minuto, segundo, weekday=0):
        self.rtc.datetime((ano, mes, dia, weekday, hora, minuto, segundo, 0))

    def agora(self):
        return self.rtc.datetime()

    def data_tuple(self):
        dt = self.agora()
        return dt[0], dt[1], dt[2]

    def hora_tuple(self):
        dt = self.agora()
        return dt[4], dt[5], dt[6]

    def data_str(self):
        ano, mes, dia = self.data_tuple()
        return "{:04d}-{:02d}-{:02d}".format(ano, mes, dia)

    def hora_str(self):
        hora, minuto, segundo = self.hora_tuple()
        return "{:02d}:{:02d}:{:02d}".format(hora, minuto, segundo)

    def data_arquivo(self):
        ano, mes, dia = self.data_tuple()
        return "{:04d}{:02d}{:02d}".format(ano, mes, dia)

    def sincronizar_online(self):
        resposta = None

        try:
            resposta = urequests.get(TIME_API_URL)

            if resposta.status_code != 200:
                print("Erro HTTP RTC:", resposta.status_code)
                return False

            dados = resposta.json()
            ano = int(dados["year"])
            mes = int(dados["month"])
            dia = int(dados["day"])
            hora = int(dados["hour"])
            minuto = int(dados["minute"])
            segundo = int(dados["seconds"])

            self.ajustar(ano, mes, dia, hora, minuto, segundo)
            print("RTC sincronizado:", self.data_str(), self.hora_str())
            return True

        except Exception as e:
            print("Falha ao sincronizar RTC:", e)
            return False

        finally:
            try:
                if resposta is not None:
                    resposta.close()
            except:
                pass