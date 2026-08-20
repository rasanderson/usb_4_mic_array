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

output_file = "/home/nras/output_doa.csv"

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
            except KeyboardInterrupt:
                break
