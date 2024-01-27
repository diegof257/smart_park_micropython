import network,time, urequests,ujson
import uasyncio as asyncio
import _thread
from machine import Pin,PWM,I2C
from utime import sleep, sleep_ms
from servo import Servo

#Servomotor
motor = Servo(15)
motor = Servo(19)
#Sensores infrarojos para ingreso y salida
pir_ing = Pin(21, Pin.IN)
pir_sal = Pin(20, Pin.IN)
#Sensores infrarojos para espacios de estacionamientos
pir_p1 = Pin(14, Pin.IN)
pir_p2 = Pin(27, Pin.IN)
pir_p3 = Pin(30, Pin.IN)
#Led RGB el espacio 1
r1 = Pin(13,Pin.OUT)
g1 = Pin(25,Pin.OUT)
b1 = Pin(17, Pin.OUT)
#Led RGB espacio 2
r2 = Pin(32, Pin.OUT)
g2 = Pin(33, Pin.OUT)
b2 = Pin(11,Pin.OUT)
#Led RGB espacio 3
r2 = Pin(32, Pin.OUT)
g2 = Pin(33, Pin.OUT)
b2 = Pin(11,Pin.OUT)

#Se crean 3 listas y se agregan los leds
lRed = [r1,r2,r3]
lGreen = [g1,g2,g3]
lBlue = [b1,b2,b3]

#Url para actualizar el estado de los espacios del parqueadero
url_base = 'https://smartparkapi-production.up.railway.app/'
urlIngresoSalida = 'https://c7eb-186-147-127-14.ngrok-free.app/historical/'

#Funciones para cambiar de verde a rojo segun el estado
def leds_rgb(r, g, b,busy):
    if busy:
        r(not 1)
        g(not 0)
        b(not 0)
    else:
        r(not 1)
        g(not 2)
        b(not 0)
    
    
# Conexion a wifi
def conWifi(red,password):
    global miRed
    miRed = network.WLAN(network.STA_IF)
    if not miRed.isconnected():
        miRed.active(True)
        miRed.connect(red,password)
        print('Conectando a la red ',red,' ...')
        timeout = time.time ()
        while not miRed.isconnected():
            if(time.ticks_diff (time.time (), timeout) > 10):
                return False
    return True

def actualizar_estado_espacios(url_base, pir_p1,pir_p2, lGreen, lRed, lBlue):
    
    while True:
        valor_p1 = pir_p1.value()
        valor_p2 = pir_p2.value()
        valor_p3 = pir_p3.value()   
        #se añaden a una lista los valores obtenidos de los espacios de parqueo
        lista_espacios = [valor_p1,valor_p2,valor_p3]
        for i in range(len(lista_espacios)):
            busy = False
            num = int(i + 1)
            # Condicion para los leds
            if lista_espacios[i] == 1:
                busy = False
            else:
                busy = True
            leds_rgb(lRed[i],lGreen[i],lBlue[i],busy)
            #Creamos el diccionario para enviarlo como un obj json
            parametros = {"number": num, "busyStatus": busy}
            url = url_base + 'telegram/status_slots/' +str(num)
            respuesta = urequests.put(url, json=parametros)
            print(respuesta.text)
            print(respuesta.status_code)
            sleep(0.6)
        
_thread.start_new_thread(actualizar_estado_espacios, (url_base, pir_p1, pir_p2,lGreen, lRed, lBlue))

def capturar_ingreso(lista_espacios,valor_pir,motor,url_base):
    if 1 in lista_espacios:
        if valor_pir == 1:
            print('Sin Movimiento')
            sleep(0.6)
            motor.move(0)
        else:
            print("Se ha detectado movimiento", valor_pir)

            placa = str(input('Ingrese la placa del vehículo: '))
            if placa != "":
                parametros = {'plate': placa }
                respuesta = urequests.post(url_base+'historical',json=parametros)
                print(respuesta.text)
                print(respuesta.status_code)
                motor.move(90)
                sleep(0.6)
    else:
        sleep(0.6)
        motor.move(0)
       

if conWifi('Three_E68658','6bV5w7Gc6BXnE65'):
    print('Conexion exitosa tu ip: ', miRed.ifconfig())
    
    while True:
        valor_pir = pir_t.value()
        
        valor_p1 = pir_p1.value()
        valor_p2 = pir_p2.value()
        valor_p3 = pir_p3.value()
        
        #se añaden a una lista los valores obtenidos de los espacios de parqueo
        lista_espacios = [valor_p1, valor_p2, valor_p3]
        
        #Llama la funcion que valida se algun vehiculo ingresó al parqueadero
        capturar_ingreso(lista_espacios,valor_pir,motor,url_base)
        
        if valor_p2 == 0:
            placa = str(input('Ingrese la placa del vehículo: '))
            if placa != "":
                parametros = {'plate': placa }
                respuesta = urequests.put(url_base+'historical/paid/',json=parametros)
                print(respuesta.text)
                print(respuesta.status_code)
                motor.move(90)
                sleep(0.6)
            else:
                sleep(0.6)
                motor.move(0)
         
        
else:
    print("Imposible conectar")
    miRed.active(False)

       
        

