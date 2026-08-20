from ctypes import *
from contextlib import contextmanager
import threading
import datetime
import time

import pyaudio
import wave

from tuning import Tuning
from mic_ports import get_mics_by_position, get_audio_index_by_position

# eink setup stuff
import sys
import os
current_dir = os.path.dirname(os.path.realpath(__file__))
libdir = os.path.join(current_dir, 'eink_files/lib')
picdir = os.path.join(current_dir, 'eink_files/pic')
if os.path.exists(libdir):
    sys.path.append(libdir)

from waveshare_epd import epd3in52
from PIL import Image, ImageDraw, ImageFont

RECORD_SECONDS = 60
RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
CHUNK = 1024
# maps mic_ports position names to the filename suffixes used for wav output
POSITION_SUFFIX = {
    "top_left": "tl",
    "top_right": "tr",
    "bottom_left": "bl",
    "bottom_right": "br",
}

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)


epd = epd3in52.EPD()
epd.init()
epd.display_NUM(epd.WHITE)
epd.lut_GC()
epd.refresh()
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
font30 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 40)

now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")
output_file = f"/home/audio/{timestamp}.csv"
output_wavs = {
    position: f"/home/audio/{timestamp}_{suffix}.wav" for position, suffix in POSITION_SUFFIX.items()
}

mics = get_mics_by_position()

with noalsaerr():
    p = pyaudio.PyAudio()

index_by_position = get_audio_index_by_position(pyaudio_instance=p, mics=mics)

streams = {
    position: p.open(
        rate=RESPEAKER_RATE,
        format=p.get_format_from_width(RESPEAKER_WIDTH),
        channels=RESPEAKER_CHANNELS,
        input=True,
        input_device_index=index,
    )
    for position, index in index_by_position.items()
}

frames_by_position = {position: [] for position in index_by_position}
stop_event = threading.Event()


def record(position):
    stream = streams[position]
    frames = frames_by_position[position]
    for _ in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
        if stop_event.is_set():
            break
        # exception_on_overflow=False: keep recording (with a gap) instead of
        # crashing the thread when the DOA/e-ink work on the main thread
        # briefly starves this thread of CPU time.
        frames.append(stream.read(CHUNK, exception_on_overflow=False))


audio_threads = [threading.Thread(target=record, args=(position,)) for position in index_by_position]
for thread in audio_threads:
    thread.start()

start_time = time.time()

with open(output_file, "a") as outfile:
    print("DateTime, ElapsedTime, DOA1bl, DOA2br, DOA3tl, DOA4tr", file=outfile)
    Mic1_tuning = Tuning(mics["bottom_left"])
    Mic2_tuning = Tuning(mics["bottom_right"])
    Mic3_tuning = Tuning(mics["top_left"])
    Mic4_tuning = Tuning(mics["top_right"])
    elapsed_seconds = time.time() - start_time
    now = datetime.datetime.now()
    print(now, ", ", f"{elapsed_seconds:.2f}", ", ", Mic1_tuning.direction, ", ", Mic2_tuning.direction, ", ", Mic3_tuning.direction, ", ", Mic4_tuning.direction, file=outfile)
    while elapsed_seconds <= RECORD_SECONDS:
        try:
            elapsed_seconds = time.time() - start_time
            now = datetime.datetime.now()
            print(now, ", ", f"{elapsed_seconds:.2f}", ", ", Mic1_tuning.direction, ", ", Mic2_tuning.direction, ", ", Mic3_tuning.direction, ", ", Mic4_tuning.direction, file=outfile)
            time.sleep(0.5)
            if int(elapsed_seconds) % 5 == 0:
                image = Image.new('1', (epd.height, epd.width), 255)
                draw = ImageDraw.Draw(image)
                draw.text((10, 20), f"Recording now {elapsed_seconds:.2f}", font=font24, fill=0)
                draw.text((10, 50), f"Mic1: {Mic1_tuning.direction:.0f} Mic2: {Mic2_tuning.direction:.0f} Mic3: {Mic3_tuning.direction:.0f} Mic4: {Mic4_tuning.direction:.0f}", font=font18, fill=0)
                epd.display(epd.getbuffer(image))
                epd.refresh()
        except KeyboardInterrupt:
            stop_event.set()
            break

stop_event.set()
for thread in audio_threads:
    thread.join()

for stream in streams.values():
    try:
        stream.stop_stream()
        stream.close()
    except OSError:
        pass  # stream may already be closed if it errored out mid-recording
p.terminate()

for position, frames in frames_by_position.items():
    wf = wave.open(output_wavs[position], 'wb')
    wf.setnchannels(RESPEAKER_CHANNELS)
    wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
    wf.setframerate(RESPEAKER_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

image = Image.new('1', (epd.height, epd.width), 255)
draw = ImageDraw.Draw(image)
draw.text((10, 10), "Sound direction angles saved to:", font=font18, fill=0)
draw.text((10, 30), f"{output_file}", font=font18, fill=0)
draw.text((10, 55), "Audio data saved to:", font=font18, fill=0)
draw.text((10, 75), f"{output_wavs['top_left']}", font=font18, fill=0)
draw.text((10, 95), f"{output_wavs['top_right']}", font=font18, fill=0)
draw.text((10, 115), f"{output_wavs['bottom_left']}", font=font18, fill=0)
draw.text((10, 135), f"{output_wavs['bottom_right']}", font=font18, fill=0)
epd.display(epd.getbuffer(image))
epd.refresh()
