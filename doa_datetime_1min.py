from tuning import Tuning
import usb.core
import usb.util
import datetime
import time

# ReSpeaker USB Mic Array IDs
VENDOR_ID = 0x2886
PRODUCT_ID = 0x0018
MAX_SECONDS = 60

output_file = "/home/nras/output_doa.csv"

# Find all devices
#dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
devices = list(usb.core.find(find_all=True, idVendor=VENDOR_ID, idProduct=PRODUCT_ID))

#for device in devices:
#    print(f"Microphone found: Bus {device.bus} Device {device.address}")


start_time = time.time()

with open(output_file, "a") as outfile:
    print("DateTime, ElapsedTime, DOA1, DOA2", file=outfile)
    if devices:
        Mic1_tuning = Tuning(devices[0])
        Mic2_tuning = Tuning(devices[1])
        elapsed_seconds = time.time() - start_time
        now = datetime.datetime.now()
        print(now,", ",f"{elapsed_seconds:.2f}", ", ", Mic1_tuning.direction, ", ", Mic2_tuning.direction, file=outfile)
        while elapsed_seconds <= MAX_SECONDS:
            try:
                elapsed_seconds = time.time() - start_time
                now = datetime.datetime.now()
                print(now,", ",f"{elapsed_seconds:.2f}", ", ", Mic1_tuning.direction, ", ", Mic2_tuning.direction, file=outfile)
                time.sleep(0.5)
            except KeyboardInterrupt:
                break
