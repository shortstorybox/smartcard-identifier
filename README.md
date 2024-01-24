# Smartcard Identifier

This is an extremely simple smartcard system that reads only the smart card's
ID number, and pastes it as text into the currently open application. This can
be used for applications that rely on nothing more than the identity of the
scanned card, such as an authentication system in a low-security environment.


# Installation: macOS

[Download for macOS](https://github.com/shortstorybox/smartcard-identifier/releases/latest)

On macOS you'll need to add permissions for simulating a keyboard:

 * Install the package above. This will add python3 to the Security settings
   which you'll enable the in the next two steps.
 * Open System Settings -> Privacy & Security -> Accessibility and enable
   permissions for python3 (and Terminal if you intend to run from a terminal).
   If you can't find python3 in the list, click the "+" button, then
   press Command+Shift+G and type /usr/bin/python3
 * Open System Settings -> Privacy & Security -> Automation and enable permissions for python3.


# Installation: Linux/Windows

    $ pip3 install smartcard-identifier
    $ smartcard-identifier --help


# Release Process

First increment the version in pyproject.toml, then run the following to build
and upload the release to Github and PyPI:

    $ make release

