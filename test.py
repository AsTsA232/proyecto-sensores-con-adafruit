from machine import Pin, I2C
import time
from bmp280 import BMP280  
from machine import SoftI2C
import ssd1306
import network
from simple import MQTTClient
import machine


#PANTALLA
bus = SoftI2C(scl=Pin(5), sda=Pin(4))
oled_width = 128
oled_height = 64
oled = ssd1306.SSD1306_I2C(oled_width, oled_height, bus)
devices = bus.scan()
if devices:
    print('Pantalla encontrada en la direccion', devices)
else:
    print('No se encontraron dispositivos I2C')


#PRESION Y TEMPERATURA
i2c = I2C(0, scl=Pin(1), sda=Pin(0),freq=40000)  
bmp = BMP280(i2c)
bmp.normal_measure()

devices = i2c.scan()
if devices:
    print('Sensor encontrado en las direccion', devices)
else:
    print('No se encontraron dispositivos I2C')
    

#SENSOR DE CALIDAD DE AIRE
anapin=machine.ADC(28)

#CONEXION A INTERNET
wlan=network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm=0xa11140)
wlan.connect("SSID","PASSWORD")

#VALIDACION DE CONEXION
while not wlan.isconnected():
    print('Error al conectarse REINTENTANDO')
    pass
print('Conectado a Wi-Fi:', wlan.ifconfig())

#CONEXION AL SERVIDOR CREDENCIALES
mqtt_host = "io.adafruit.com"
mqtt_username = "" 
mqtt_password = ""  

#VALORES DE LA RASSPBERRY A LA NUBE
calidadaire = "teresahurtado/feeds/data"  
temperatura = "teresahurtado/feeds/data-temp"  
presion = "teresahurtado/feeds/data-presion"  
idcliente = "AsTsA1" 


cliente = MQTTClient(
        client_id=idcliente,
        server=mqtt_host,
        user=mqtt_username,
        password=mqtt_password)

       
cliente.connect()

#CICLO PRINCIPAL
try:
    while True:  
        oled.fill(0)
        temp_pantalla = bmp.temperature
        pres_pantalla = bmp.pressure
        sensor_aire=anapin.read_u16()

#MEDICIONES EN CONSOLA
        print("Temperatura: {:.2f} C".format(temp_pantalla))
        print("Presion: {:.2f} hPa".format(pres_pantalla))
        print("prescencia de gases valor:  ", sensor_aire )



#VALORES EN LA OLED
        oled.text('Temperatura:', 0, 0)
        oled.text("{:.2f} C".format(temp_pantalla), 30, 10)
        oled.text('Presion:', 0, 20)
        oled.text("{:.2f} hpa".format(pres_pantalla), 20, 30)
        oled.text('Calidad del aire:', 0, 40)

#REQUIERE CALIBRACION
        if sensor_aire>30000:
            oled.text('Mala', 40, 50)
        else:
            oled.text('Buena', 40, 50)
        oled.show()

#ENVIO A LA NUBE
        cliente.publish(calidadaire, str(sensor_aire))
        cliente.publish(temperatura, str(temp_pantalla))
        cliente.publish(presion, str(pres_pantalla))
        time.sleep(10)
except Exception as e:
    print(f'Failed to publish message: {e}')
finally:
    cliente.disconnect()


#verificar modulos
#import sys
#print(sys.version)
#help("modules")