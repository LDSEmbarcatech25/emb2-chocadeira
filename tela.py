import ssd1306

OLED_ADDR = 0x3C
OLED_WIDTH = 128
OLED_HEIGHT = 64

def criar_display(i2c):
    return ssd1306.SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c, addr=OLED_ADDR)

def tela_inicial(display):
    display.fill(0)
    display.text("CHOCADEIRA", 24, 16, 1)
    display.text("RESIDENCIA", 24, 32, 1)
    display.text("EMBARCATECH", 20, 48, 1)
    display.show()

def tela_info(display, temp_amb, umidade, temp_caixa, ir_detectado, rele_ligado, ventoinha_ligada, setpoint, sd_ok):
    display.fill(0)
    display.text("=== INFO ===", 0, 0, 1)
    
    txt_ta = "Ta:{:.1f}C".format(temp_amb) if temp_amb is not None else "Ta:ERR"
    txt_u = "U:{:.0f}%".format(umidade) if umidade is not None else "U:ERR"
    display.text(txt_ta, 0, 12, 1)
    display.text(txt_u, 74, 12, 1)

    txt_tc = "Tc:{:.1f}C".format(temp_caixa) if temp_caixa is not None else "Tc:---"
    txt_ir = "IR:ON" if ir_detectado else "IR:OFF"
    display.text(txt_tc, 0, 24, 1)
    display.text(txt_ir, 74, 24, 1)

    display.text("R1:{}".format("ON" if rele_ligado else "OFF"), 0, 36, 1)
    display.text("FAN:{}".format("ON" if ventoinha_ligada else "OFF"), 64, 36, 1)

    display.text("SP:{:.1f}".format(setpoint), 0, 48, 1)
    display.text("SD:OK" if sd_ok else "SD:ERR", 80, 48, 1)
    display.show()