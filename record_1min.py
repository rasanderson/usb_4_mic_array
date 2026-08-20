from ctypes import *
from contextlib import contextmanager
import threading
import pyaudio
import wave
import datetime

from mic_ports import get_audio_index_by_position

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


RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6 # change base on firmwares, 1_channel_firmware.bin as 1 or 6_channels_firmware.bin as 6
RESPEAKER_WIDTH = 2
CHUNK = 1024
RECORD_SECONDS = 60
# maps mic_ports position names to the filename suffixes requested by the user
POSITION_SUFFIX = {
    "top_left": "tl",
    "top_right": "tr",
    "bottom_left": "bl",
    "bottom_right": "br",
}

now = datetime.datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M")

with noalsaerr():
    p = pyaudio.PyAudio()

index_by_position = get_audio_index_by_position(pyaudio_instance=p)

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


def record(position):
    stream = streams[position]
    frames = frames_by_position[position]
    for _ in range(0, int(RESPEAKER_RATE / CHUNK * RECORD_SECONDS)):
        frames.append(stream.read(CHUNK))


threads = [threading.Thread(target=record, args=(position,)) for position in index_by_position]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

for stream in streams.values():
    stream.stop_stream()
    stream.close()
p.terminate()

for position, frames in frames_by_position.items():
    output_wav = f"/home/audio/{timestamp}_{POSITION_SUFFIX[position]}.wav"
    wf = wave.open(output_wav, 'wb')
    wf.setnchannels(RESPEAKER_CHANNELS)
    wf.setsampwidth(p.get_sample_size(p.get_format_from_width(RESPEAKER_WIDTH)))
    wf.setframerate(RESPEAKER_RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

