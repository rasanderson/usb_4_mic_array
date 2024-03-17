from tuning import Tuning
import usb.core
import usb.util
import datetime
import time

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)
devices = usb.core.find(find_all=True, idVendor=0x2886, idProduct=0x0018)
print(devices)

for device in devices:
    print(f"Microphone found: Bus {device.bus} Device {device.address}")


start_time = time.time()

if dev:
    Mic_tuning = Tuning(dev)
    elapsed_seconds = time.time() - start_time
    now = datetime.datetime.now()
    print(now,", ",f"{elapsed_seconds:.2f}", ", ", Mic_tuning.direction)
    while True:
        try:
            elapsed_seconds = time.time() - start_time
            now = datetime.datetime.now()
            print(now,", ",f"{elapsed_seconds:.2f}", ", ", Mic_tuning.direction)
            time.sleep(1.5)
        except KeyboardInterrupt:
            break
