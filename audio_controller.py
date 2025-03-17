#!/usr/bin/python
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
from pijuice import PiJuice
pijuice = PiJuice()

epd = epd3in52.EPD()
epd.init()
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)
  
while True:
    # Create a new image
    image = Image.new('1', (epd.height, epd.width), 255)
    draw = ImageDraw.Draw(image)
    # Get battery percentage
    battery_percent = pijuice.status.GetChargeLevel()['data']
    # Draw text into the image
    draw.text((10,0), 'Ready to record audio...', font = font24, fill=0)
    draw.text((10,20), f"Battery percentage: {battery_percent}%", font = font24, fill=0)
    # Display on e-ink screen
    epd.display(epd.getbuffer(image))
    epd.refresh()
    # Update after 60 seconds
    time.sleep(60)
