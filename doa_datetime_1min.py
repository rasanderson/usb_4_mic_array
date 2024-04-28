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


with open('/sys/bus/usb/devices/1-1.3/devnum', 'r') as file:
    usb_bl = int(file.read().strip())
with open('/sys/bus/usb/devices/1-1.5/devnum', 'r') as file:
    usb_br = int(file.read().strip())
with open('/sys/bus/usb/devices/1-1.2/devnum', 'r') as file:
    usb_tl = int(file.read().strip())
with open('/sys/bus/usb/devices/1-1.4/devnum', 'r') as file:
    usb_tr = int(file.read().strip())

devices[0].address = usb_bl
devices[1].address = usb_br
devices[2].address = usb_tl
devices[3].address = usb_tr

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
            except KeyboardInterrupt:
                break
