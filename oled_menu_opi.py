from OPi import GPIO
from PIL import ImageFont, ImageDraw
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from time import sleep
import socket
import sys_info
import time

clk = 22
dt = 21
sw = 29

global gdraw, gdevice, menuindex, flag_menu
flag_menu = False
menuindex = 0

GPIO.setboard(GPIO.PCPCPLUS)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(sw, GPIO.IN, pull_up_down=GPIO.PUD_UP)
serial = i2c(port=0, address=0x3C)
device = ssd1306(serial, rotate=0)

clkLastState = 0
clkState = 0

def ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = (s.getsockname()[0])
        s.close()
        return str(ip)   
    except:
        return "IP no encontrada"
	
def invert(draw,x,y,text):
    font = ImageFont.load_default()
    draw.rectangle((x, y, x+120, y+10), outline=255, fill=255)
    draw.text((x, y), text, font=font, outline=0,fill="black")
	
# Box and text rendered in portrait mode
def menu(device, draw, menustr, index):
    print "..........INIT............"
    font = ImageFont.load_default()
    draw.rectangle(device.bounding_box, outline="white", fill="black")
    for i in range(len(menustr)):
        if( i == index):
            menuindex = i
            invert(draw, 2, i*10, menustr[i])
        else:
		    draw.text((2, i*10), menustr[i], font=font, fill=255)
		
		
names = ['Memory', 'Disk', 'IPAddress', 'Network', 'CPUUsage', 'Settings']
with canvas(device) as draw:
    menu(device, draw, names, 0)

def menu_operation(strval):
    global menuindex, flag_menu
    if ( strval == "Memory"):
        flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), sys_info.mem_usage(), fill="white")
            #draw.text((30, 60), back(), fill="white")        
    if ( strval == "Disk"):
        flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), sys_info.disk_usage('/'), fill="white")
            #draw.text((30, 60), back(), fill="white")        
    if ( strval == "Network"):
        flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), sys_info.network('wlan0'), fill="white")
    if ( strval == "CPUUsage"):
        flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), sys_info.cpu_usage(), fill="white")
    if ( strval == "IPAddress"):
        flag_menu = True
        with canvas(device) as draw:
            draw.text((0, 26), ip_address(), fill="white")
    if ( strval == "Settings"):
        flag_menu = True
        with canvas(device) as draw:
            #draw.rectangle(device.bounding_box, outline="white", fill="black")
            draw.text((0, 26), "Spanish", fill="white")
            draw.text((0, 52), "English", fill="white")       

def sw_callback(channel):
    global flag_menu 
    global menuindex
    if flag_menu:
        menu_update()
        flag_menu = True
    strval = names[menuindex]
    menu_operation(strval)
    
    
clkLastState = GPIO.input(clk)

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
        abs(menuindex)
        menu_update()
        clkLastState = clkState
        sleep(0.01)

def menu_update():
    global menuindex
    with canvas(device) as draw:
        menu(device, draw, names, menuindex%6)       
        
try:
    GPIO.add_event_detect(sw, GPIO.FALLING , callback=sw_callback, bouncetime=100)
    GPIO.add_event_detect(clk, GPIO.FALLING , callback=rotary_callback, bouncetime=100)  
    raw_input("Enter anything") 
except KeyboardInterrupt:  
    print "Keyboard Interrupt"
	# here you put any code you want to run before the program   
	# exits when you press CTRL+C  
    GPIO.cleanup()
except:  
	# this catches ALL other exceptions including errors.  
	# You won't get any error messages for debugging  
	# so only use it once your code is working  
    print "Ending"  
    GPIO.cleanup()
finally:  
    print "Finally"  
    GPIO.cleanup() # this ensures a clean exit		 
		

#GPIO.cleanup()
