# ============================================================
# CONFIGURACOES GERAIS DA KIIRA
# ============================================================

# Wi-Fi
WIFI_SSID = "IFCE"
WIFI_SENHA = "ifcewifi"
PORTA_HTTP = 80

# RTC online
TIME_API_URL = "https://timeapi.io/api/Time/current/zone?timeZone=America/Sao_Paulo"

# Controle de Temperatura
SETPOINT = 37.5

# Ventoinha
ATRASO_VENT_LIGA_MS = 1000
ATRASO_VENT_DESLIGA_MS = 1000

# I2C compartilhado: HDC1080 + OLED
PIN_I2C_SDA = 14
PIN_I2C_SCL = 21
I2C_FREQ = 100_000

# Botao
PIN_BOTAO_TELA = 45

# Saidas
PIN_RELE = 47
PIN_VENTOINHA = 48
PIN_BUZZER = 3 # Buzzer da placa Kiira

# SD Card em SDMMC 1-bit
PIN_SD_CLK = 39
PIN_SD_CMD = 38
PIN_SD_D0 = 40

# Novos Sensores
PIN_INFRAVERMELHO = 41
PIN_DS18B20 = 42

# Intervalo de log em ms
INTERVALO_LOG_MS = 5000