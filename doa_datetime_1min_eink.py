from tuning import Tuning
import usb.core
import usb.util
import datetime
import time
from mic_ports import get_mics_by_position

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

mics = get_mics_by_position()

start_time = time.time()

with open(output_file, "a") as outfile:
    print("DateTime, ElapsedTime, DOA1bl, DOA2br, DOA3tl, DOA4tr", file=outfile)
    if mics:
        Mic1_tuning = Tuning(mics["bottom_left"])
        Mic2_tuning = Tuning(mics["bottom_right"])
        Mic3_tuning = Tuning(mics["top_left"])
        Mic4_tuning = Tuning(mics["top_right"])
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
