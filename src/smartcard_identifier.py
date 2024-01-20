#!/usr/bin/env python3
import platform
import sys
import time
from binascii import hexlify
from subprocess import PIPE, Popen

import smartcard.util
from smartcard.scard import (INFINITE, SCARD_E_TIMEOUT, SCARD_PROTOCOL_T0,
                             SCARD_PROTOCOL_T1, SCARD_S_SUCCESS,
                             SCARD_SCOPE_USER, SCARD_SHARE_SHARED,
                             SCARD_STATE_PRESENT, SCARD_STATE_UNAWARE,
                             SCARD_UNPOWER_CARD, SCardConnect, SCardDisconnect,
                             SCardEstablishContext, SCardGetErrorMessage,
                             SCardGetStatusChange, SCardListReaders,
                             SCardReleaseContext, SCardTransmit)

TIMEOUT = 15  # seconds
SYSTEM = None


def platform_system():
    global SYSTEM
    if not SYSTEM:
        SYSTEM = platform.system()
    return SYSTEM


def simulate_keypress(text):
    """
    Paste the given text into the current application.
    """
    if not text.replace("\n", "").replace(" ", "").isalnum():
        raise Exception(
            "Keystroke text must be alphanumeric with spaces/newlines allowed"
        )

    if platform_system() == "Darwin":
        cmd = [
            "osascript",
            "-e",
            f'tell application "System Events" to keystroke "{text}"',
        ]
    elif platform_system() == "Linux":
        cmd = ["xdotool", "type", "--delay", "0", text]
    elif platform_system() == "Windows":
        cmd = [
            "powershell",
            "-Command",
            f'[System.Windows.Forms.SendKeys]::SendWait("{text}")',
        ]
    else:
        raise Exception(f"Unsupported platform: {platform.system()}")

    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print(f'Failed to simulate keypress: {stderr.decode("utf-8")}')


def process_card(context, reader):
    """
    Process a card that was inserted into the reader.
    """
    result, card, protocol = SCardConnect(
        context, reader, SCARD_SHARE_SHARED, SCARD_PROTOCOL_T0 | SCARD_PROTOCOL_T1
    )
    if result != SCARD_S_SUCCESS:
        print(f"Failed to connect to card: {SCardGetErrorMessage(result)}")
        return
    try:
        QUERY_CARD_ID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
        result, response = SCardTransmit(card, protocol, QUERY_CARD_ID)
        if result != SCARD_S_SUCCESS:
            print(f"Failed to read card ID: {SCardGetErrorMessage(result)}")
            return
        card_id = hexlify(bytes(response)).decode("ascii").upper()[:14]
        simulate_keypress(card_id + "\n")
    finally:
        result = SCardDisconnect(card, SCARD_UNPOWER_CARD)
        if result != SCARD_S_SUCCESS:
            print("Failed to disconnect: {SCardGetErrorMessage(result)}")


def run(context):
    """
    Run the main loop that waits for a card reader to be connected to the
    computer, and for a card to be inserted into the reader.
    """

    readers, readerstates = [], []
    while True:
        previous_readers = readers
        while True:
            result, readers = SCardListReaders(context, [])
            if result != SCARD_S_SUCCESS:
                sys.exit(
                    f"Failed to determine if there are NFC readers: {SCardGetErrorMessage(result)}"
                )
            if readers:
                break
            else:
                time.sleep(TIMEOUT)

        if readers != previous_readers:
            # Re-initialize readerstates to account for new and/or removed readers
            result, readerstates = SCardGetStatusChange(
                context, 0, [(r, SCARD_STATE_UNAWARE) for r in readers]
            )
            if result != SCARD_S_SUCCESS:
                sys.exit(
                    f"Failed to get NFC reader status: {SCardGetErrorMessage(result)}"
                )

        while True:
            if not readerstates:
                raise AssertionError(
                    "readerstates is empty, which should be impossible"
                )
            result, readerstates = SCardGetStatusChange(
                context, TIMEOUT * 1000, readerstates
            )
            if result == SCARD_S_SUCCESS:
                for reader, eventstate, atr in readerstates:
                    if eventstate & SCARD_STATE_PRESENT:
                        process_card(context, reader)
            elif result == SCARD_E_TIMEOUT:
                break  # restart loop to check if a new reader was connected to the computer
            else:
                sys.exit(
                    f"Failed to get NFC reader status: {SCardGetErrorMessage(result)}"
                )


if __name__ == "__main__":
    result, context = SCardEstablishContext(SCARD_SCOPE_USER)
    if result != SCARD_S_SUCCESS:
        sys.exit(f"Failed to establish NFC context: {SCardGetErrorMessage(result)}")

    try:
        run(context)
    finally:
        result = SCardReleaseContext(context)
        if result != SCARD_S_SUCCESS:
            sys.exit(f"Failed to release NFC context: {SCardGetErrorMessage(result)}")
