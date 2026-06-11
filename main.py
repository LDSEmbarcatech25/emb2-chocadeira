import machine
from machine import Pin, SoftI2C, PWM
import time
import network
import socket
import ujson
import os 

from config import (
    WIFI_SSID, WIFI_SENHA, PORTA_HTTP,
    SETPOINT,
    ATRASO_VENT_LIGA_MS, ATRASO_VENT_DESLIGA_MS,
    PIN_I2C_SDA, PIN_I2C_SCL, I2C_FREQ,
    PIN_RELE, PIN_VENTOINHA, PIN_BUZZER,
    PIN_SD_CLK, PIN_SD_CMD, PIN_SD_D0,
    PIN_INFRAVERMELHO, PIN_DS18B20, INTERVALO_LOG_MS
)

from hdc1080 import HDC1080
from ds18b20 import SensorDS18B20
from infravermelho import SensorInfravermelho
from tela import criar_display, tela_inicial, tela_info
from controle import ControleRele, ControleVentoinha
from rtc_utils import RelogioRTC
from logger_sd import LoggerSD
from camera_service import CameraService

# Inicialização do Barramento I2C
i2c = SoftI2C(sda=Pin(PIN_I2C_SDA), scl=Pin(PIN_I2C_SCL), freq=I2C_FREQ)

# Instanciação dos periféricos base
sensor = HDC1080(i2c)
display = criar_display(i2c)

tela_inicial(display)
time.sleep(3)

sensor_caixa = SensorDS18B20(PIN_DS18B20)
sensor_ir = SensorInfravermelho(PIN_INFRAVERMELHO)

lampada = ControleRele(PIN_RELE, "LAMPADA")
ventoinha = ControleVentoinha(PIN_VENTOINHA, "VENTOINHA", ATRASO_VENT_LIGA_MS, ATRASO_VENT_DESLIGA_MS)

# Configuração do Buzzer (GPIO 3 a 5 kHz de acordo com a Kiira)
buzzer = PWM(Pin(PIN_BUZZER))
buzzer.freq(5000)
buzzer.duty_u16(0)

relogio = RelogioRTC()
logger = LoggerSD(PIN_SD_CLK, PIN_SD_CMD, PIN_SD_D0, relogio)
sd_ok = logger.montar()

# Inicialização do Módulo de Câmara OV5640
try:
    camera = CameraService()
    print("Câmara OV5640 inicializada com sucesso.")
except Exception as e:
    print("Erro ao inicializar câmara:", e)
    camera = None

# Temporizadores não bloqueantes (Janelas de Execução)
ultimo_log_ms = time.ticks_ms()
ultima_leitura_sensores_ms = time.ticks_ms() - 10000  # Força primeira leitura no arranque
ultima_foto_tampa_aberta_ms = 0  
ultimo_print_ms = 0  

# Variáveis globais de dados em cache
ultima_temperatura = None
ultima_umidade = None
temp_caixa = None
estado_ir = 0

# Flags de controlo e lógica de transição de estado
forcar_lampada = False
forcar_ventoinha = False
tampa_estava_aberta = False  

# Recuperação automática do último ficheiro guardado no SD após reinicialização
nome_ultima_foto = "Nenhuma"
if sd_ok:
    try:
        arquivos = [f for f in os.listdir("/sd") if f.startswith("abertura_") and f.endswith(".jpeg")]
        if arquivos:
            arquivos.sort() 
            nome_ultima_foto = arquivos[-1]
            print("Última foto detetada no Cartão SD:", nome_ultima_foto)
    except Exception as e:
        print("Erro ao varrer diretório do SD:", e)

def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    wlan.disconnect()
    time.sleep(1)

    try:
        print("A estabelecer ligação ao Wi-Fi...")
        wlan.connect(WIFI_SSID, WIFI_SENHA)

        tentativas = 0
        while not wlan.isconnected() and tentativas < 20:
            time.sleep(1.5) 
            tentativas += 1

        if wlan.isconnected():
            config = wlan.ifconfig()
            print("====================================")
            print("Wi-Fi Conectado com Sucesso! IP:", config[0])
            print("====================================")
            return wlan
        return None

    except Exception as e:
        print("Erro crítico no rádio Wi-Fi:", e)
        return None

def atualizar_sistema():
    global ultima_temperatura, ultima_umidade, temp_caixa, estado_ir, ultimo_log_ms
    global forcar_lampada, forcar_ventoinha, tampa_estava_aberta, nome_ultima_foto
    global ultima_leitura_sensores_ms, ultima_foto_tampa_aberta_ms, ultimo_print_ms

    agora_ms = time.ticks_ms()

    # =========================================================================
    # 1. MONITORIZAÇÃO IMEDIATA E CONTÍNUA (Prioridade de segurança)
    # =========================================================================
    estado_ir = sensor_ir.status()                
    tampa_aberta = (estado_ir == 0)

    # Gestão de Capturas Fotográficas (Borda de subida ou intervalo de 5 min)
    if tampa_aberta:
        tirar_foto_agora = False
        
        if not tampa_estava_aberta:
            print(">>> EVENTO: Tampa aberta detetada! A capturar imagem... <<<")
            tirar_foto_agora = True
        elif time.ticks_diff(agora_ms, ultima_foto_tampa_aberta_ms) >= 300000:
            print(">>> EVENTO: Tampa permanece aberta há 5 minutos! Nova captura... <<<")
            tirar_foto_agora = True
            
        if tirar_foto_agora:
            if sd_ok and camera is not None:
                hora_formatada = relogio.hora_str().replace(":", "")
                nome_simples = "abertura_{}_{}.jpeg".format(relogio.data_arquivo(), hora_formatada)
                caminho_completo = "/sd/" + nome_simples
                try:
                    camera.bater_foto_salvar(caminho_completo)
                    nome_ultima_foto = nome_simples 
                    ultima_foto_tampa_aberta_ms = agora_ms 
                except Exception as e:
                    print("Erro ao guardar imagem no SD:", e)
            elif not sd_ok:
                print("Aviso: Cartão SD indisponível para gravação de imagem.")
            elif camera is None:
                print("Aviso: Sensor de câmara offline.")

    tampa_estava_aberta = tampa_aberta 

    # =========================================================================
    # 2. JANELA DE LEITURA DOS SENSORES A CADA 10 SEGUNDOS (Estabilidade de Barramento)
    # =========================================================================
    if time.ticks_diff(agora_ms, ultima_leitura_sensores_ms) >= 10000:
        ultima_temperatura = sensor.ler_temperatura() 
        ultima_umidade = sensor.ler_umidade()
        
        t_caixa = sensor_caixa.atualizar()
        if t_caixa is not None:
            temp_caixa = t_caixa
            
        ultima_leitura_sensores_ms = agora_ms

    elif sensor_caixa.convertendo:
        t_caixa = sensor_caixa.atualizar()
        if t_caixa is not None:
            temp_caixa = t_caixa

    # =========================================================================
    # 3. VERIFICAÇÃO DE ALARMES E GESTÃO DE ATUADORES
    # =========================================================================
    alarme_ativado = False
    if temp_caixa is not None and temp_caixa > (SETPOINT + 4.0):
        alarme_ativado = True

    if alarme_ativado:
        buzzer.duty_u16(32768)  # Ativa o tom de emergência térmica
    else:
        buzzer.duty_u16(0)      

    # Lógica de Acionamento da Lâmpada (Manual / Setpoint)
    if forcar_lampada:
        if not lampada.estado(): lampada.ligar()
    else:
        lampada.atualizar_por_setpoint(temp_caixa, SETPOINT, tampa_aberta)

    # Lógica de Acionamento da Ventoinha (Manual / Setpoint + 1°C)
    if forcar_ventoinha:
        if not ventoinha.estado(): ventoinha.ligar()
    else:
        ventoinha.atualizar_por_setpoint(temp_caixa, SETPOINT, tampa_aberta)

    # Atualização contínua do OLED
    tela_info(display, ultima_temperatura, ultima_umidade, temp_caixa, not tampa_aberta, lampada.estado(), ventoinha.estado(), SETPOINT, sd_ok)

    # Escrita Periódica no Cartão SD
    if time.ticks_diff(agora_ms, ultimo_log_ms) >= INTERVALO_LOG_MS:
        ultimo_log_ms = agora_ms
        logger.salvar(ultima_temperatura, ultima_umidade, temp_caixa, not tampa_aberta, lampada.estado(), ventoinha.estado())

    # Saída Filtrada no Terminal a cada 2 segundos para evitar poluição visual
    if time.ticks_diff(agora_ms, ultimo_print_ms) >= 2000:
        ultimo_print_ms = agora_ms
        print("Ta:{}C U:{}% Tc:{}C IR:{} Lamp:{} Vent:{} Alarme:{}".format(
            ultima_temperatura, ultima_umidade, temp_caixa, 
            "FECHADA(1)" if not tampa_aberta else "ABERTA(0)",
            "ON" if lampada.estado() else "OFF", 
            "ON" if ventoinha.estado() else "OFF",
            "CRÍTICO" if alarme_ativado else "OK"))

def json_status(ip):
    return ujson.dumps({
        "data": relogio.data_str(),
        "hora": relogio.hora_str(),
        "temp_amb_c": ultima_temperatura,
        "umidade": ultima_umidade,
        "temp_caixa_c": temp_caixa,
        "ir_detectado": estado_ir == 1,
        "lampada": lampada.estado(),
        "ventoinha": ventoinha.estado(),
        "setpoint": SETPOINT,
        "sd_ok": sd_ok,
        "ip": ip,
        "forcar_lampada": forcar_lampada,
        "forcar_ventoinha": forcar_ventoinha,
        "ultima_foto": nome_ultima_foto
    })

def responder_json(cliente, corpo):
    try:
        cliente.sendall(b"HTTP/1.1 200 OK\r\n")
        cliente.sendall(b"Access-Control-Allow-Origin: *\r\n")
        cliente.sendall(b"Connection: close\r\n")
        cliente.sendall(b"Content-Type: application/json\r\n\r\n")
        cliente.sendall(corpo.encode('utf-8'))
    except:
        pass

def responder_404(cliente):
    try:
        cliente.sendall(b"HTTP/1.1 404 Not Found\r\n")
        cliente.sendall(b"Connection: close\r\n\r\n")
    except:
        pass

def iniciar_servidor(wlan):
    addr = socket.getaddrinfo("0.0.0.0", PORTA_HTTP)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(2)
    s.settimeout(0.2)

    ip = wlan.ifconfig()[0]
    print("Servidor HTTP ativo em: http://{}:{}".format(ip, PORTA_HTTP))

    while True:
        atualizar_sistema()
        try:
            cliente, endereco = s.accept()
        except OSError:
            continue

        try:
            req = cliente.recv(1024).decode('utf-8')
            if not req:
                cliente.close()
                continue
                
            linha = req.split("\r\n")[0]
            partes = linha.split(" ")
            rota = partes[1] if len(partes) > 1 else "/"

            if rota == "/api/status":
                responder_json(cliente, json_status(ip))
                
            elif rota == "/api/force/lampada":
                global forcar_lampada
                forcar_lampada = not forcar_lampada 
                responder_json(cliente, ujson.dumps({"status": "ok", "forcar_lampada": forcar_lampada}))
                
            elif rota == "/api/force/ventoinha":
                global forcar_ventoinha
                forcar_ventoinha = not forcar_ventoinha 
                responder_json(cliente, ujson.dumps({"status": "ok", "forcar_ventoinha": forcar_ventoinha}))
                
            elif rota == "/api/reset":
                responder_json(cliente, ujson.dumps({"status": "resetando"}))
                time.sleep(1) 
                machine.reset() 
                
            elif rota.startswith("/api/foto/recente"):
                global nome_ultima_foto
                if nome_ultima_foto == "Nenhuma":
                    responder_404(cliente)
                else:
                    caminho_foto = "/sd/" + nome_ultima_foto
                    try:
                        tamanho = os.stat(caminho_foto)[6]
                        
                        cliente.sendall(b"HTTP/1.1 200 OK\r\n")
                        cliente.sendall(b"Access-Control-Allow-Origin: *\r\n")
                        cliente.sendall(b"Content-Type: image/jpeg\r\n")
                        cliente.sendall(b"Connection: close\r\n")
                        cliente.sendall("Content-Length: {}\r\n\r\n".format(tamanho).encode('utf-8'))
                        
                        # Transmissão por blocos de 2KB para otimizar velocidade e RAM
                        with open(caminho_foto, "rb") as f:
                            while True:
                                bloco = f.read(2048)
                                if not bloco: break
                                cliente.write(bloco) 
                    except Exception as e:
                        print("Erro na transmissão binária da imagem:", e)
                        
            elif rota == "/api/csv":
                try:
                    cliente.sendall(b"HTTP/1.1 200 OK\r\n")
                    cliente.sendall(b"Access-Control-Allow-Origin: *\r\n")
                    cliente.sendall(b"Connection: close\r\n")
                    cliente.sendall(b"Content-Type: text/csv; charset=utf-8\r\n\r\n")
                    for bloco in logger.ler_arquivo_stream():
                        cliente.sendall(bloco.encode('utf-8'))
                except:
                    pass
            else:
                responder_404(cliente)

        except:
            pass
        finally:
            try:
                cliente.close()
            except:
                pass

print("Firmware de inicialização ativado.")
wlan = conectar_wifi()

if wlan:
    relogio.sincronizar_online()
    iniciar_servidor(wlan)
else:
    print("Modo Offline ativo por falha de rede Wi-Fi.")
    relogio.ajustar(2026, 6, 11, 14, 30, 0)
    while True:
        atualizar_sistema()
        time.sleep_ms(200)
