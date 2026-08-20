"""Shared helper to reliably map ReSpeaker mics to physical Pi ports.

port_numbers reflects the physical USB hub topology (stable across
reboots), unlike device address/devnum which is assigned dynamically.
Run list_usb_ports.py to confirm/update PORT_MAP for your specific Pi.
"""
import glob
import os
import re

import usb.core

VENDOR_ID = 0x2886
PRODUCT_ID = 0x0018

PORT_MAP = {
    "top_left": (1, 1, 2),
    "top_right": (1, 3),
    "bottom_left": (1, 1, 3),
    "bottom_right": (1, 2),
}

# Extracts the ALSA card number from a PyAudio device name such as
# "ReSpeaker 4 Mic Array (UAC1.0): USB Audio (hw:2,0)".
_HW_CARD_RE = re.compile(r"hw:(\d+)")


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


def _usb_sysfs_fragment(device):
    """Build the kernel sysfs path component for a USB device, e.g. '1-1.3'."""
    return f"{device.bus}-{'.'.join(str(p) for p in device.port_numbers)}"


def _alsa_card_by_position(mics):
    """Map position -> ALSA card number by resolving each card's USB sysfs path."""
    fragment_to_position = {_usb_sysfs_fragment(device): position for position, device in mics.items()}

    card_by_position = {}
    for device_link in glob.glob("/sys/class/sound/card*/device"):
        card_num = int(re.search(r"card(\d+)", device_link).group(1))
        real_path = os.path.realpath(device_link)
        for fragment, position in fragment_to_position.items():
            if f"/{fragment}:" in real_path or real_path.endswith(f"/{fragment}"):
                card_by_position[position] = card_num
                break

    return card_by_position


def get_audio_index_by_position(pyaudio_instance=None):
    """Map position -> PyAudio input device index for the 4 ReSpeaker boards.

    Uses the same USB port_numbers-based identification as get_mics_by_position(),
    correlated to ALSA card numbers via sysfs, then to PyAudio device indices
    (since all 4 boards share an identical PyAudio device name).
    """
    import pyaudio

    mics = get_mics_by_position()
    card_by_position = _alsa_card_by_position(mics)

    missing = [position for position in mics if position not in card_by_position]
    if missing:
        raise RuntimeError(
            f"Could not resolve ALSA card for positions {missing}. "
            f"Run list_audio_ports.py to inspect the USB/ALSA/PyAudio mapping."
        )

    owns_instance = pyaudio_instance is None
    p = pyaudio_instance or pyaudio.PyAudio()
    try:
        index_by_card = {}
        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if info.get("maxInputChannels", 0) <= 0:
                continue
            match = _HW_CARD_RE.search(info.get("name", ""))
            if match:
                index_by_card[int(match.group(1))] = i

        missing = [
            position for position, card in card_by_position.items() if card not in index_by_card
        ]
        if missing:
            raise RuntimeError(
                f"Could not find a PyAudio input device for positions {missing} "
                f"(resolved ALSA cards: {card_by_position}). "
                f"Run list_audio_ports.py to inspect the USB/ALSA/PyAudio mapping."
            )

        return {position: index_by_card[card] for position, card in card_by_position.items()}
    finally:
        if owns_instance:
            p.terminate()
