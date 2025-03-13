#!/usr/bin/env python3
import argparse
import getpass
import platform
import shutil
import sys
import time
from binascii import hexlify
from subprocess import PIPE, Popen

from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardConnectionException, NoCardException

_system = None


def platform_system():
    global _system
    if not _system:
        _system = platform.system()
    return _system


_last_simulated_keypress = 0


def simulate_keypress(text, use_linux_uinput, osx_control_modifier=False):
    """
    Paste the given text into the current application.
    """
    without_special_characters = (
        text.replace("\n", "").replace(" ", "").replace(":", "").replace("\u00a7", "")
    )
    if without_special_characters and not without_special_characters.isalnum():
        raise Exception(
            "Keystroke text must be alphanumeric (spaces/newlines/colon allowed)"
        )

    if platform_system() == "Darwin":
        cmd = [
            "osascript",
            "-e",
            f'tell application "System Events" to keystroke "{text}"{" using control down" if osx_control_modifier else ""}',
        ]
    elif platform_system() == "Linux":
        if use_linux_uinput:
            cmd = ["ydotool", "type", "--next-delay", "0", "--key-delay", "0", text]
        else:
            cmd = ["xdotool", "type", "--delay", "0", text]
    elif platform_system() == "Windows":
        cmd = [
            "powershell",
            "-Command",
            f'[System.Windows.Forms.SendKeys]::SendWait("{text}")',
        ]
    else:
        raise Exception(f"Unsupported platform: {platform.system()}")

    global _last_simulated_keypress
    if _last_simulated_keypress > time.time() - 0.1:
        # This helps reduce certain race conditions on certain platforms
        # when keypresses are simulated too quickly.
        time.sleep(0.1)
        _last_simulated_keypress = time.time()

    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
    except FileNotFoundError:
        sys.stderr.write(
            f'ERROR: Could not find command "{cmd[0]}". Please install it on your system.\n'
        )
        return
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        sys.stderr.write("Failed to simulate keypress: ")
        sys.stderr.write(stderr.decode())
        sys.stderr.write("\n")
        sys.stderr.flush()


def run(print_only, use_linux_uinput):
    cardrequest = CardRequest(timeout=None, newcardonly=True)
    while True:
        card = cardrequest.waitforcard()
        try:
            try:
                card.connection.connect()
            except NoCardException as err:
                sys.stderr.write(f"{err}\n")
                sys.stderr.flush()
                continue

            QUERY_CARD_ID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            try:
                response, sw1, sw2 = card.connection.transmit(QUERY_CARD_ID)
            except CardConnectionException as err:
                sys.stderr.write(f"{err}\n")
                sys.stderr.flush()
                continue

            SUCCESS = (0x90, 0x00)
            if (sw1, sw2) == SUCCESS:
                card_id = hexlify(bytes(response)).decode("ascii").upper()
                if print_only:
                    print(card_id)
                else:
                    simulate_keypress(card_id + "\n", use_linux_uinput=use_linux_uinput)
            else:
                sys.stderr.write("Failed to read card ID\n")
                sys.stderr.flush()
        finally:
            card.connection.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description="Wait for a smart card to be scanned, then emulate a keyboard to paste the card ID as text."
    )
    parser.add_argument(
        "--test-permissions",
        action="store_true",
        help="Check if Accessibility & Automation permissions are set up correctly. (macOS only)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--x11",
        action="store_true",
        help="Use X11 to simulate keypresses. (Linux only)",
    )
    group.add_argument(
        "--uinput",
        action="store_true",
        help="Use uinput to simulate keypresses. Requires user to be in the 'input' group, or to run as root. (Linux only)",
    )
    group.add_argument(
        "--stdout",
        action="store_true",
        help="Print the card ID to stdout instead of simulating keypresses.",
    )
    args = parser.parse_args()
    if args.test_permissions:
        if platform_system() != "Darwin":
            sys.exit("ERROR: --test-permissions is only supported on macOS")
        try:
            simulate_keypress(
                "\u00a7", use_linux_uinput=False, osx_control_modifier=True
            )
        except Exception as err:
            sys.exit(f"ERROR: {err}")
        else:
            sys.exit("OK")

    if platform_system() == "Linux":
        if args.uinput:
            shutil.which("ydotool") or sys.exit(
                "Please install `ydotool`, e.g.:\n\n    $ sudo apt-get install ydotoold ydotool"
            )
        elif args.x11:
            shutil.which("xdotool") or sys.exit(
                "Please install `xdotool`, e.g.:\n\n    $ sudo apt-get install xdotool"
            )
        elif args.stdout:
            pass
        else:
            parser.print_help()
            sys.exit("ERROR: You must specify either --x11 or --uinput or --stdout")

    def do_run(*_, **__):
        run(print_only=args.stdout, use_linux_uinput=args.uinput)

    if args.stdout:
        # Disable keyboard echoing on the terminal, which can cause confusion
        # if the script is running at the same time somewhere else
        _raw_input = getpass._raw_input
        try:
            getpass._raw_input = do_run
            getpass.getpass("")
        finally:
            getpass._raw_input = _raw_input
    else:
        do_run()


if __name__ == "__main__":
    main()
