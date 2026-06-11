from machine import Pin, SDCard
import os

class LoggerSD:
    def __init__(self, pin_clk, pin_cmd, pin_d0, relogio):
        self.pin_clk = pin_clk
        self.pin_cmd = pin_cmd
        self.pin_d0 = pin_d0
        self.relogio = relogio
        self.montado = False
        self.sd = None

    def montar(self):
        if self.montado:
            return True

        try:
            self.sd = SDCard(slot=1, width=1, sck=Pin(self.pin_clk), cmd=Pin(self.pin_cmd), data=(Pin(self.pin_d0),))

            try:
                os.mount(self.sd, "/sd")
            except OSError:
                try:
                    os.umount("/sd")
                except:
                    pass
                os.mount(self.sd, "/sd")

            self.montado = True
            print("SD montado com sucesso.")
            print("Conteudo /sd:", os.listdir("/sd"))
            return True

        except Exception as e:
            self.montado = False
            self.sd = None
            print("Erro ao montar SD:", e)
            return False

    def desmontar(self):
        try:
            os.umount("/sd")
            self.montado = False
            self.sd = None
            print("SD desmontado.")
            return True
        except Exception as e:
            print("Erro ao desmontar SD:", e)
            return False

    def esta_montado(self):
        return self.montado

    def nome_arquivo(self):
        return "/sd/lote_{}.csv".format(self.relogio.data_arquivo())

    def garantir_arquivo(self):
        caminho = self.nome_arquivo()
        try:
            os.stat(caminho)
        except OSError:
            with open(caminho, "w") as f:
                f.write("data,hora,temp_amb_c,umidade,temp_caixa_c,ir_detectado,rele,ventoinha\n")
        return caminho

    def salvar(self, temp_amb, umidade, temp_caixa, ir_detectado, rele_ligado, ventoinha_ligada):
        if not self.montado:
            print("SD nao montado. Nao foi possivel salvar.")
            return False
        try:
            caminho = self.garantir_arquivo()
            t_amb_str = "" if temp_amb is None else "{:.1f}".format(temp_amb)
            u_str = "" if umidade is None else "{:.1f}".format(umidade)
            t_cx_str = "" if temp_caixa is None else "{:.1f}".format(temp_caixa)
            
            linha = "{},{},{},{},{},{},{},{}\n".format(
                self.relogio.data_str(), self.relogio.hora_str(), 
                t_amb_str, u_str, t_cx_str, 
                1 if ir_detectado else 0, 1 if rele_ligado else 0, 1 if ventoinha_ligada else 0
            )
            with open(caminho, "a") as f:
                f.write(linha)
            return True
        except Exception as e:
            print("Erro ao salvar no CSV:", e)
            return False

    def listar_arquivos(self):
        if not self.montado:
            print("SD nao montado.")
            return []
        try:
            return os.listdir("/sd")
        except Exception as e:
            print("Erro ao listar arquivos do SD:", e)
            return []

    def ler_arquivo_stream(self, caminho=None, tamanho_bloco=512):
        cabecalho_vazio = "data,hora,temp_amb_c,umidade,temp_caixa_c,ir_detectado,rele,ventoinha\n"
        if not self.montado:
            print("SD nao montado.")
            yield cabecalho_vazio
            return
            
        if caminho is None:
            caminho = self.nome_arquivo()
            
        try:
            with open(caminho, "r") as f:
                while True:
                    bloco = f.read(tamanho_bloco)
                    if not bloco:
                        break
                    yield bloco
        except Exception as e:
            print("Erro ao ler arquivo stream:", e)
            yield cabecalho_vazio