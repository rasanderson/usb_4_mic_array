from tuning import Tuning
import usb.core
import usb.util
import time

dev = usb.core.find(idVendor=0x2886, idProduct=0x0018)

start_time = time.time()

if dev:
    Mic_tuning = Tuning(dev)
    elapsed_seconds = time.time() - start_time
    print(f"{elapsed_seconds:.2f}", " ", Mic_tuning.direction)
    while True:
        try:
            elapsed_seconds = time.time() - start_time
            print(f"{elapsed_seconds:.2f}", " ", Mic_tuning.direction)
            time.sleep(0.5)
        except KeyboardInterrupt:
            break
