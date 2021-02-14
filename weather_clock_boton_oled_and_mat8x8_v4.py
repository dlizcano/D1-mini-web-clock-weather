
import framebuf
gc.collect()
import time
gc.collect()
import machine
gc.collect()
import neopixel
gc.collect()
import network
gc.collect()
import urequests
gc.collect()
import utime
gc.collect()
from machine import RTC, I2C, Pin
#from ssd1306 import SSD1306_I2C
import sh1106 #Oled
gc.collect()
import freesans20 # letter 20
gc.collect()
import icons8x8
gc.collect()
import writer # escribe letra y grafico
gc.collect()

n = 64 # 8x8=64
p = 14 # pin d1
np = neopixel.NeoPixel(machine.Pin(p), n)

#Delay for showing image
delay = 15

#Clear the screen
def clear():
    for i in range(64):
        np[i] = (0x00, 0x00, 0x00)
        np.write()

clear()
# display cool guy
for values in icons8x8.cool:
    np[values] = (255, 255, 0)
    np[16]= (0x99,0x99,0x99)
    np[21]= (0x99,0x99,0x99)
    np.write()
sleep(7)


def load_image(filename):
    with open(filename, 'rb') as f:
        f.readline()
        f.readline()
        width, height = [int(v) for v in f.readline().split()]
        data = bytearray(f.read())
    return framebuf.FrameBuffer(data, width, height, framebuf.MONO_HLSB)

# SSD1106 OLED display
print("Connecting to wifi...")
display = sh1106.SH1106_I2C(128, 64, I2C(scl=Pin(5), sda=Pin(4), freq=400000))
#display.fill(1)

#importa font y grafico .pbm
font_writer = writer.Writer(display, freesans20) 
temperature_pbm = load_image('temperature.pbm')
#humidity_pbm = load_image('humidity.pbm')


#display en Oled           
display.fill(0)
display.text("Connecting", 0, 5)
display.text(" to wifi...", 0, 15)
display.show()
time.sleep_ms(3000) # Espera 3 segundos

#Setup WiFi
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.connect("LIZCANO", "Paris2006")
print(sta.isconnected())

#display(3)
display.fill(0)
display.text("Connected !!!", 0, 5)
display.text(" to wifi...", 0, 15)
display.show()

# wifi connected
print("IP:", sta.ifconfig()[0], "\n")
display.text(" IP: ", 0, 35)
display.text(" " + str(sta.ifconfig()[0]), 0, 45)
display.show()

# clock data
url = "http://worldtimeapi.org/api/timezone/America/Bogota" # see http://worldtimeapi.org/timezones
web_query_delay = 60000 # interval time of web JSON query
retry_delay = 3000 # interval time of retry after a failed Web query
# internal real time clock
rtc = RTC()

# set timer
update_time = utime.ticks_ms() - web_query_delay

#setup the button
button = machine.Pin(13, machine.Pin.IN, machine.Pin.PULL_UP)

# Confirma OK
clear()
for values in icons8x8.ok1:
    np[values] = (20, 200, 20) 
    np.write()
for values in icons8x8.ok2:
    np[values] = (20, 50, 20)
    np.write()
sleep(8)
clear() # clear ok

      
display.fill(0)
display.show() # apaga oled        


while True:
    print(button.value())
    if button.value() == 0:
        # clock loop
        while button.value() == 0: # True:
            # if lose wifi connection, reboot ESP8266
            if not sta.isconnected():
                machine.reset()
            # query and get web JSON every web_query_delay ms
            if utime.ticks_ms() - update_time >= web_query_delay:
        
                # HTTP GET data
                response = urequests.get("http://worldtimeapi.org/api/timezone/America/Bogota")
            
                if response.status_code == 200: # query success
                
                    print("JSON response:\n", response.text)
                    
                    # parse JSON
                    parsed = response.json()
                    datetime_str = str(parsed["datetime"])
                    year = int(datetime_str[0:4])
                    month = int(datetime_str[5:7])
                    day = int(datetime_str[8:10])
                    hour = int(datetime_str[11:13])
                    minute = int(datetime_str[14:16])
                    second = int(datetime_str[17:19])
                    subsecond = int(round(int(datetime_str[20:26]) / 10000))
                
                    # update internal RTC
                    rtc.datetime((year, month, day, 0, hour, minute, second, subsecond))
                    update_time = utime.ticks_ms()
                    print("RTC updated\n")
           
                else: # query failed, retry retry_delay ms later
                    update_time = utime.ticks_ms() - web_query_delay + retry_delay
            
            # generate formated date/time strings from internal RTC
            date_str = "{1:02d}/{2:02d}/{0:4d}".format(*rtc.datetime())
            time_str = "{4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime())

            # update SSD1306 OLED display
            display.fill(0)
            #display.text("WebClock", 0, 5)
            textlen_h = font_writer.stringlen(time_str)
            textlen_d = font_writer.stringlen(date_str)
            font_writer.set_textpos((128 - textlen_h) // 2, 10)
            font_writer.printstring(time_str)
            
            #font_writer.set_textpos((128 - textlen_d) // 2, 50)
            #font_writer.printstring(date_str)
            display.text(date_str, 25, 55)
            #display.text(time_str, 0, 45)
            display.show()
            
            utime.sleep(0.1)

    if button.value() == 1:
        r = urequests.get("http://api.openweathermap.org/data/2.5/weather?q=Cajica,CO&appid=a2200cf760d109aeb26996d0188b06c9&units=metric").json()
        weather = r["weather"][0]["main"]
        weather2 = r["weather"][0]["description"]
        temp = r["main"]["temp"]
        print(weather)
        print(weather2)
        print(temp)
        display.fill(0) # apaga oled 
        display.show() # apaga oled
        if weather == "Clear":
            for values in icons8x8.sun0:
                np[values] = (0x4c, 0x99, 0x00)
                np.write()
            sleep(1)
            for values in icons8x8.sun1:
                np[values] = (0x4c, 0x99, 0x00)
                np.write()
            sleep(1)
            for values in icons8x8.sun2:
                np[values] = (0x4c, 0x99, 0x00)
                np.write()
                sleep(0.2)
            sleep(delay)
            # cool guy
            clear() # clear neopixel
            for values in icons8x8.cool:
                np[values] = (255, 255, 0)
            np.write()
            np[16]= (0x99,0x99,0x99)
            np[21]= (0x99,0x99,0x99)
            sleep(0.3)
            np.write()
            np[16]= (0,0,0)
            np[21]= (0,0,0)
            sleep(0.3)
            np[16]= (0x99,0x99,0x99)
            np[21]= (0x99,0x99,0x99)
            sleep(0.3)
            np.write()
            sleep(delay)
            display.fill(0) # apaga oled 
            display.show() # apaga oled 
            clear() # clear neopixel
        elif weather2 == "few clouds":
            display.text("Outside: ", 0, 10)
            display.text(weather2, 0, 20)
            display.text("Temperature: " + str(temp), 0, 40)
            #display.text(str(temp), 35, 35)
            #display.text(" to wifi...", 0, 15)
            display.show()
            for values in icons8x8.fewclouds1:
                np[values] = (0x99, 0x99, 0x99)
                np.write()
            for values in icons8x8.fewclouds2:
                np[values] = (0x25, 0x25, 0x25)
                np.write()
            for values in icons8x8.fewclouds3:
                np[values] = (250,140,0)
                np.write()
            sleep(0.5)
            for values in icons8x8.fewclouds4:
                np[values] = (250, 250, 0)
                np.write()
                sleep(0.2)
            sleep(delay)
            display.fill(0) # apaga oled 
            display.show() # apaga oled 
            clear() # clear neopixel
        elif weather2 == "scattered clouds":
            display.text("Outside: ", 0, 10)
            display.text(weather2, 0, 20)
            display.text("Temperature: " + str(temp), 0, 40)
            #display.text(str(temp), 35, 35)
            #display.text(" to wifi...", 0, 15)
            display.show()
            for values in icons8x8.fewclouds1:
                np[values] = (0x99, 0x99, 0x99)
                np.write()
            for values in icons8x8.fewclouds2:
                np[values] = (0x25, 0x25, 0x25)
                np.write()
            for values in icons8x8.fewclouds3:
                np[values] = (250,140,0)
                np.write()
            sleep(0.5)
            for values in icons8x8.fewclouds4:
                np[values] = (250, 250, 0)
                np.write()
                sleep(0.2)
            sleep(delay)
            display.fill(0) # apaga oled 
            display.show() # apaga oled 
            clear() # clear neopixel
        elif weather2 == "broken clouds":
            display.text("Outside: ", 0, 10)
            display.text(weather2, 0, 20)
            display.text("Temperature: " + str(temp), 0, 40)
            #display.text(str(temp), 35, 35)
            #display.text(" to wifi...", 0, 15)
            display.show()
            for values in icons8x8.cloudy:
                np[values] = (0x99, 0x99, 0x99)
                np.write()
            sleep(delay)
            display.fill(0) # apaga oled 
            display.show() # apaga oled 
            clear() # clear neopixel
        elif weather == "Rain":
            display.text("Outside: ", 0, 10)
            display.text(weather2, 0, 20)
            display.text("Temperature: " + str(temp), 0, 40)
            for values in icons8x8.cloudy:
                np[values] = (0x55, 0x55, 0x55)
                np.write()
                sleep(1)
            for values in icons8x8.rain:
                np[values] = (0x00, 0x00, 0x99)
                np.write()
            sleep(delay)
            display.fill(0) # apaga oled 
            display.show() # apaga oled 
            clear()
        elif weather == "Thunderstorm":
            display.text("Outside: ", 0, 10)
            display.text(weather2, 0, 20)
            display.text("Temperature: " + str(temp), 0, 40)
            for values in icons8x8.cloudy:
                np[values] = (0x55, 0x55, 0x55)
                np.write()
                sleep(1)
            for values in icons8x8.lightning1:
                np[values] = (250, 250, 0x00)
                np.write()
            for values in icons8x8.lightning2:
                np[values] = (250, 153, 0)
                np.write()
            sleep(delay)
            display.fill(0) # apaga oled 
            display.show() # apaga oled 
            clear()
        elif weather == "Snow":
            display.text("Outside: ", 0, 10)
            display.text(weather2, 0, 20)
            display.text("Temperature: " + str(temp), 0, 40)
            for values in icons8x8.snow_ice:
                np[values] = (0x00, 0x00, 0x99)
                np.write()
            sleep(delay)
            display.fill(0) # apaga oled 
            display.show() # apaga oled 
            clear()
    sleep(1)