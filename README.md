# Smartcard Identifier

This is an extremely simple smartcard system that reads only the smart card's
ID number, and pastes it as text into the currently open application. This can
be used for applications that rely on nothing more than the ID of the
scanned card.


# Installation: macOS

[Download for macOS](https://github.com/shortstorybox/smartcard-identifier/releases/latest)

 * Install the package above. This will also add python3 to the security settings
   which you'll enable the in the next two steps.
 * Open System Settings -> Privacy & Security -> Automation and enable permissions for python3.
 * Open System Settings -> Privacy & Security -> Accessibility and enable permissions for python3.

If you can't find python3 in the list, click the "+" button, then
press Command+Shift+G and type /usr/bin/python3

# Installation: Linux/Windows

https://pypi.org/project/smartcard-identifier/

    $ pip3 install smartcard-identifier
    $ smartcard-identifier --help


# Release Process

To sign the macOS release you will need to have the relevant Developer
Certificate installed in your Keychain, which you can download from
https://developer.apple.com/account/resources/certificates/list . Make sure
you also have Apple's intermediate certificates installed, which you can download
from the bottom of the page at
https://developer.apple.com/account/resources/certificates/add . Without these,
the Developer Certificate will show up as "untrusted" in Keychain Access.


To build & publish a release, first increment the version in pyproject.toml,
then run the following to build and upload to Github and PyPI:

    $ make release

# Notes

If you run into the following error installing via `pip3 install smartcard-identifier` on macOS:

    × Building wheel for pyscard (pyproject.toml) did not run successfully.
    │ exit code: 1
    ╰─> [5 lines of output]
        running bdist_wheel
        running build
        running build_py
        Install swig and try again

then you can fix the above error by running `brew install swig`.
