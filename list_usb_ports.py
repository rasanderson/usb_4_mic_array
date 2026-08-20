"""Print bus/address/port_numbers for connected ReSpeaker mics.

Run this with mics connected (one at a time, or all four) to discover
which port_numbers tuple corresponds to each physical port (top-left,
top-right, bottom-left, bottom-right) on your specific Raspberry Pi.
Use the results to populate PORT_MAP in mic_ports.py.
"""
import usb.core

VENDOR_ID = 0x2886
PRODUCT_ID = 0x0018

# Confirmed positions for this Pi (see mic_ports.PORT_MAP); re-verify if
# mics are moved to different physical ports or on a different Pi.
KNOWN_DEFAULTS = {
    (1, 1, 2): "top_left",
    (1, 3): "top_right",
    (1, 1, 3): "bottom_left",
    (1, 2): "bottom_right",
}

devices = list(usb.core.find(find_all=True, idVendor=VENDOR_ID, idProduct=PRODUCT_ID))

if not devices:
    print("No ReSpeaker devices found.")
else:
    print(f"Found {len(devices)} device(s):\n")
    for device in devices:
        guess = KNOWN_DEFAULTS.get(device.port_numbers, "unknown")
        print(f"bus={device.bus} address={device.address} port_numbers={device.port_numbers} guessed_position={guess}")
