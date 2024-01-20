all: SmartcardIdentifier.pkg

.PHONY: build/package.pkg
build/package.pkg:
	rm -rf build/
	mkdir -p build/package/usr/local/bin/ build/package/Library/LaunchAgents/
	# The script must run using the built-in system version of Python
	echo '#!/usr/bin/python3' | cat - src/smartcard_identifier.py > build/package/usr/local/bin/smartcard-identifier
	chmod +x build/package/usr/local/bin/smartcard-identifier
	cp macOS/com.shortstorybox.SmartcardIdentifier.plist build/package/Library/LaunchAgents/
	pkgbuild --root build/package --identifier com.shortstorybox.SmartcardIdentifier --version "$$(cat VERSION)" --ownership recommended --scripts macOS/scripts build/package.pkg

SmartcardIdentifier.pkg: build/package.pkg
	productbuild --distribution macOS/distribution.xml --package-path build/ SmartcardIdentifier.pkg

.PHONY: clean
clean:
	rm -rf build/
	rm -f SmartcardIdentifier.pkg

