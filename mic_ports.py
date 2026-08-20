"""Shared helper to reliably map ReSpeaker mics to physical Pi ports.

port_numbers reflects the physical USB hub topology (stable across
reboots), unlike device address/devnum which is assigned dynamically.
Run list_usb_ports.py to confirm/update PORT_MAP for your specific Pi.
"""
import usb.core

VENDOR_ID = 0x2886
PRODUCT_ID = 0x0018

PORT_MAP = {
    "top_left": (1, 1, 2),
    "top_right": (1, 3),
    "bottom_left": (1, 1, 3),
    "bottom_right": (1, 2),
}


def get_mics_by_position():
    devices = list(usb.core.find(find_all=True, idVendor=VENDOR_ID, idProduct=PRODUCT_ID))
    devices_by_port = {device.port_numbers: device for device in devices}

    missing = [position for position, port in PORT_MAP.items() if port not in devices_by_port]
    if missing:
        raise RuntimeError(
            f"Expected mics at positions {missing} but they were not found "
            f"({len(devices)} device(s) detected). Run list_usb_ports.py and "
            f"check PORT_MAP in mic_ports.py."
        )

    return {position: devices_by_port[port] for position, port in PORT_MAP.items()}
