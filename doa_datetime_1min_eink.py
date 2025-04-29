from tuning import Tuning
import usb.core
import usb.util
import datetime
import time

# ReSpeaker USB Mic Array IDs
VENDOR_ID = 0x2886
PRODUCT_ID = 0x0018
MAX_SECONDS = 60

# eink setup stuff
import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(current_dir, 'eink_files/lib')
picdir = os.path.join(current_dir, 'eink_files/pic')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd3in52
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

epd = epd3in52.EPD()
epd.init()
epd.display_NUM(epd.WHITE)
epd.lut_GC()
epd.refresh()
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)

#output_file = "/home/nras/output_doa.csv"
now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")
output_file = f"/home/audio/{timestamp}.csv"
output_wav = f"/home/audio/{timestamp}.wav"

# Find all devices
#dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
devices = list(usb.core.find(find_all=True, idVendor=VENDOR_ID, idProduct=PRODUCT_ID))

#for device in devices:
#    print(f"Microphone found: Bus {device.bus} Device {device.address}")

# Need to chagne next 8 lines as device numbers not always
# consistent between different Rpi machines
#with open('/dev/bus/usb/001/008', 'r') as file:
#    content = file.read().strip()
#    print(content)
#    usb_bl = int(file.read().strip())
#with open('/dev/bus/usb/001/006', 'r') as file:
#    usb_br = int(file.read().strip())
#with open('/sys/bus/usb/001/004', 'r') as file:
#    usb_tl = int(file.read().strip())
#with open('/sys/bus/usb/001/005', 'r') as file:
#    usb_tr = int(file.read().strip())
#devices[0].address = usb_bl
#devices[1].address = usb_br
#devices[2].address = usb_tl
#devices[3].address = usb_tr

# Revised using pyudev
#context = pyudev.Context()
#devices = []
# Find ReSpeaker microphones
#for device in context.list_devices(subsystem='usb'):
#    if 'ID_MODEL' in device and 'ReSpeaker' in device.get('ID_MODEL'):
#        devices.append(device)
#if len(devices) != 4:
#    raise Exception("Expected 4 microphones but found {}".format(len(devices)))
# Assign addresses
#for i, device in enumerate(devices):
#    devices[i].address = int(device.device_number)


# Modified usb.core approach
devices = list(usb.core.find(find_all=True, idVendor=VENDOR_ID, idProduct=PRODUCT_ID))
if len(devices) != 4:
    raise Exception("Expected 4 microphones but found {}".format(len(devices)))
for i, device in enumerate(devices):
    devices[i].address - device.address
                              
start_time = time.time()

with open(output_file, "a") as outfile:
    print("DateTime, ElapsedTime, DOA1bl, DOA2br, DOA3tl, DOA4tr", file=outfile)
    if devices:
        Mic1_tuning = Tuning(devices[0])
        Mic2_tuning = Tuning(devices[1])
        Mic3_tuning = Tuning(devices[2])
        Mic4_tuning = Tuning(devices[3])
        elapsed_seconds = time.time() - start_time
        now = datetime.datetime.now()
        print(now,", ",f"{elapsed_seconds:.2f}", ", ", Mic1_tuning.direction, ", ", Mic2_tuning.direction, ", ", Mic3_tuning.direction,", ", Mic4_tuning.direction, file=outfile)
        while elapsed_seconds <= MAX_SECONDS:

            try:
                elapsed_seconds = time.time() - start_time
                now = datetime.datetime.now()
                print(now,", ",f"{elapsed_seconds:.2f}", ", ", Mic1_tuning.direction, ", ", Mic2_tuning.direction, ", ", Mic3_tuning.direction,", ", Mic4_tuning.direction, file=outfile)
                time.sleep(0.5)
                if int(elapsed_seconds) % 5 == 0:
                    # Create info for eink display
                    image = Image.new('1', (epd.height, epd.width), 255)
                    draw = ImageDraw.Draw(image)
                    draw.text((10,20), f"Recording now {elapsed_seconds:.2f}", font = font24, fill=0)
                    draw.text((10,50), f"Mic1: {Mic1_tuning.direction:.0f} Mic2: {Mic2_tuning.direction:.0f} Mic3: {Mic3_tuning.direction:.0f} Mic4: {Mic4_tuning.direction:.0f}", font = font18, fill=0)
                    epd.display(epd.getbuffer(image))
                    epd.refresh()
            except KeyboardInterrupt:
                break

image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)
draw.text((10,20), f"Sound direction angles saved to:", font = font24, fill=0)
draw.text((10,50), f"{output_file}", font = font18, fill=0)
draw.text((10,90), f"Audio data saved to:", font = font24, fill=0)
draw.text((10,120), f"{output_wav}", font = font18, fill=0)
epd.display(epd.getbuffer(image))
epd.refresh()
