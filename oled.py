#!/ust/bin/env python
# -*- coding: utf-8 -*-

from OPi import GPIO
from PIL import Image, ImageFont, ImageDraw
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from time import sleep
import socket
import sys_info
import time
import sys
import os.path
from demo_opts import get_device

clk = 15
dt = 13
sw = 11

global gdraw, gdevice, menuindex, flag_menu
flag_menu = False
menuindex = 0

GPIO.setboard(GPIO.PCPCPLUS)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)

clkLastState = 0
clkState = 0
swState = 0

## Shows the IP address
def ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = (s.getsockname()[0])
        s.close()
        return str(ip)   
    except:
        return "IP no encontrada"
	
def logo(device):
    img_path = os.path.abspath(os.path.join(os.path.dirname(__file__),
        'images', 'decroly.png'))
    logo = Image.open(img_path).convert("RGBA")
    fff = Image.new(logo.mode, logo.size, (255,) * 4)

    background = Image.new("RGBA", device.size, "white")
    posn = ((device.width - logo.width) // 2, 0)
    while True:
        if (GPIO.event_detected(clk) == False or GPIO.event_detected(sw) == False):
            sleep (10)
            for angle in range(0, 360, 2):
                rot = logo.rotate(angle, resample=Image.BILINEAR)
                img = Image.composite(rot, fff, rot)
                background.paste(img, posn)
                device.display(background.convert(device.mode))
        else:
            menu_update()

def invert(draw,x,y,text):
    font = ImageFont.load_default()
    draw.rectangle((x, y, x+120, y+10), outline=255, fill=255)
    draw.text((x, y), text, font=font, outline=0,fill="black")
	
# Box and text rendered in portrait mode
def menu(device, draw, menustr, index):
    #print "..........INIT............"
    font = ImageFont.load_default()
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    for i in range(len(menustr)):
        if( i == index):
            menuindex = i
            invert(draw, 2, i*10, menustr[i])
        else:
            draw.text((2, i*10), menustr[i], font=font, fill=255)
		
#names = ['Memoria virtual', 'Memoria interna', 'Direccion IP', 'Network', 'CPU Usage', 'Settings']
names = ['Memoria virtual', 'Memoria interna', 'Direccion IP', 'Network', 'CPU Usage']    
    
def back_to_menu(device, draw):
    invert(draw, 0, 5, "Volver")
    if swState == 1:
        flag_menu = False
        with canvas(device) as draw:
            menu(device, draw, names, 0)


def menu_operation(strval):
    global menuindex, flag_menu
    if ( strval == "Memoria virtual"):
        #flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), sys_info.mem_usage(), fill="white")      
            back_to_menu(device, draw)
    if ( strval == "Memoria interna"):
        #flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), sys_info.disk_usage('/'), fill="white")
            #draw.text((0, 26), disk.render, fill="white")
            back_to_menu(device, draw)       
    if ( strval == "Network"):
        #flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), sys_info.network('wlan0'), fill="white")
            back_to_menu(device, draw)
    if ( strval == "CPU Usage"):
        #flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), sys_info.cpu_usage(), fill="white")
            back_to_menu(device, draw)
    if ( strval == "Direccion IP"):
        #flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), ip_address(), fill="white")
            back_to_menu(device, draw) 
    #if ( strval == "Settings"):
        #flag_menu = True
        #logo(device)          
            #draw.rectangle(device.bounding_box, outline="white", fill="black")
            #draw.text((0, 26), "Spanish", fill="white")
            #draw.text((0, 52), "English", fill="white")     

def sw_callback(channel):
    global flag_menu 
    global menuindex
    if flag_menu:
        with canvas(device) as draw:
            menu(device, draw, names, 0)
        flag_menu = True
    else:
        strval = names[menuindex]
        menu_operation(strval)
        flag_menu = False

def rotary_callback(channel):
    global clkLastState
    global menuindex
	
    if flag_menu == False:
		
        clkState = GPIO.input(clk)
        dtState = GPIO.input(dt)
		
        if dtState != clkState:
            menuindex -= 1
        else:
            menuindex += 1
			
        menuindex = abs(menuindex)
		menuindex = menuindex % len(names)
        menu_update()
        clkLastState = clkState
        sleep(0.01)

def menu_update():
    global menuindex
	global names
	
    with canvas(device) as draw:
        menu(device, draw, names, menuindex)

def main():
    swState = GPIO.input(clk)
    clkLastState = GPIO.input(clk)

    GPIO.add_event_detect(sw, GPIO.FALLING , callback=sw_callback, bouncetime=100)
    GPIO.add_event_detect(clk, GPIO.FALLING , callback=rotary_callback, bouncetime=100)

    with canvas(device) as draw:
        menu(device, draw, names, 0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('Shutting down...!')
        GPIO.cleanup()
