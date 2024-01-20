# Smartcard Identifier

This is an extremely simple smartcard system that reads only the smart card's
ID number, and pastes it as text into the currently open application. This can
be used for applications that rely on nothing more than the identity of the
scanned card, such as an authentication system in a low-security environment.

Smartcard Identifier is implemented in Python and is compatible with Linux,
macOS, and Windows. Currently only the installer for macOS is implemented; on
other systems you'll have to run the Python script from a terminal.


# Release Process

To build the macOS package installer, first increment the VERSION file and then
run the following:

    $ make SmartcardIdentifier.pkg

