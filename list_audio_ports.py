"""Print the resolved position -> ALSA card -> PyAudio index mapping.

Run this with all four mics connected to verify get_audio_index_by_position()
picks the correct PyAudio input device for each physical position before
relying on it in record_1min.py.
"""
from ctypes import *
from contextlib import contextmanager

import pyaudio

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


with noalsaerr():
    p = pyaudio.PyAudio()


print("All PyAudio input devices:")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info.get("maxInputChannels", 0) > 0:
        print(f"  index={i} name={info.get('name')!r}")

print()
try:
    index_by_position = get_audio_index_by_position(pyaudio_instance=p)
except RuntimeError as exc:
    print(f"Mapping failed: {exc}")
else:
    print("Resolved position -> PyAudio index:")
    for position, index in index_by_position.items():
        name = p.get_device_info_by_index(index).get("name")
        print(f"  {position}: index={index} name={name!r}")

p.terminate()
