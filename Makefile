all: SmartcardIdentifier.pkg dist

build/package.pkg: lint pyproject.toml src/smartcard_identifier.py macOS/com.shortstorybox.SmartcardIdentifier.plist
	rm -rf build/
	mkdir -p build/package/usr/local/bin/ build/package/Library/LaunchAgents/
	cp macOS/com.shortstorybox.SmartcardIdentifier.plist build/package/Library/LaunchAgents/
	# The script must run using the built-in system version of Python
	echo '#!/usr/bin/python3' | cat - src/smartcard_identifier.py > build/package/usr/local/bin/smartcard-identifier
	chmod +x build/package/usr/local/bin/smartcard-identifier
	pkgbuild --root build/package --identifier com.shortstorybox.SmartcardIdentifier \
		--version "$$(grep '^version *= *' pyproject.toml|sed 's/^version *= *//;s/\"//g')" \
		--ownership recommended --scripts macOS/scripts build/package.pkg

SmartcardIdentifier.pkg: build/package.pkg macOS/distribution.xml
	@rm -rf build/signed.pkg
	@productbuild --distribution macOS/distribution.xml --package-path build/ \
		     --sign 'Developer ID Installer: Short Story, Inc. (PD7WK7PS94)' build/signed.pkg || ( \
		echo '\033[31m\n\nSigning failed. Please install the "Developer ID Application" certificate' \
		     'into Keychain Access. Download from:\n\n' \
		     '    - https://developer.apple.com/account/resources/certificates/list\033[0m'; \
		exit 1)
	@xcrun notarytool submit build/signed.pkg --wait --keychain-profile 'notary-profile' || ( \
		echo '\033[31m\n\nNotarization failed. Please store credentials in Keychain Access as follows:\n\n' \
		    '    1. Create an app-specific password at https://account.apple.com/account/manage\n' \
		    '    2. $$ xcrun notarytool store-credentials notary-profile --team-id PD7WK7PS94 --apple-id YOUR-EMAIL@YOUR-DOMAIN.com\n\033[0m'; \
		exit 1)
	xcrun stapler staple build/signed.pkg
	mv build/signed.pkg SmartcardIdentifier.pkg

install: .install
.install:
	@HOMEBREW_NO_AUTO_UPDATE=1 brew install --quiet twine python-build ruff gh && touch .install

.PHONY: dist
dist: lint install
	rm -rf dist/
	python3 -m build

.PHONY: lint
lint: install
	ruff check --no-fix src/
	ruff format --quiet --check src/

.PHONY: fix
fix: install
	ruff check --fix src/
	ruff format --quiet src/

.PHONY: release
release: dist SmartcardIdentifier.pkg install
	@git diff --exit-code || (echo "Please commit your git changes before releasing."; exit 1)
	@git diff --cached --exit-code || (echo "Please commit your git changes before releasing."; exit 1)
	@echo 'Uploading release to Github...'
	@GH_PROMPT_DISABLED= gh release create --target="$$(git rev-parse HEAD)" \
		--title=v"$$(grep '^version *= *' pyproject.toml|sed 's/^version *= *//;s/\"//g')" \
		--generate-notes v"$$(grep '^version *= *' pyproject.toml|sed 's/^version *= *//;s/\"//g')" \
		SmartcardIdentifier.pkg
	@echo
	@if [ ! -e ~/.pypirc ]; \
	 then echo "Please create a PyPI API token: https://pypi.org/manage/account/token/"; \
	      echo "Then save it to your ~/.pypirc file, or enter it as your PyPI password below."; \
	      echo "Press Enter to continue..."; \
	      read waiting; \
	 fi
	twine upload --username __token__ 'dist/*'

.PHONY: clean
clean:
	rm -rf build/ dist/
	rm -f SmartcardIdentifier.pkg .install

