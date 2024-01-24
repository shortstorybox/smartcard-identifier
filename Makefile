all: SmartcardIdentifier.pkg dist

.PHONY: build/package.pkg
build/package.pkg: lint
	rm -rf build/
	mkdir -p build/package/usr/local/bin/ build/package/Library/LaunchAgents/
	# The script must run using the built-in system version of Python
	echo '#!/usr/bin/python3' | cat - src/smartcard_identifier.py > build/package/usr/local/bin/smartcard-identifier
	chmod +x build/package/usr/local/bin/smartcard-identifier
	cp macOS/com.shortstorybox.SmartcardIdentifier.plist build/package/Library/LaunchAgents/
	pkgbuild --root build/package --identifier com.shortstorybox.SmartcardIdentifier \
		--version "$$(grep '^version *= *' pyproject.toml|sed 's/^version *= *//;s/\"//g')" \
		--ownership recommended --scripts macOS/scripts build/package.pkg

SmartcardIdentifier.pkg: build/package.pkg macOS/distribution.xml
	productbuild --distribution macOS/distribution.xml --package-path build/ SmartcardIdentifier.pkg

.PHONY: dist
dist: lint
	rm -rf dist/
	python3 -m pip install build
	python3 -m build

.PHONY: lint
lint:
	python3 -m pip install ruff black isort
	python3 -m ruff src/
	python3 -m black --check src/ || (echo "Please run 'make format' to fix formatting issues."; exit 1)
	python3 -m isort src/ || (echo "Please run 'make format' to fix formatting issues."; exit 1)

.PHONY: format
format:
	python3 -m pip install black isort
	python3 -m black src/
	python3 -m isort src/

.PHONY: release
release: dist SmartcardIdentifier.pkg
	which gh >/dev/null || (echo "The 'gh' command is missing. Please install the GitHub CLI: https://cli.github.com/"; exit 1)
	@echo 'Uploading release to Github...'
	@GH_PROMPT_DISABLED= gh release create --target="$$(git rev-parse HEAD)" \
		--title=v"$$(grep '^version *= *' pyproject.toml|sed 's/^version *= *//;s/\"//g')" \
		--generate-notes v"$$(grep '^version *= *' pyproject.toml|sed 's/^version *= *//;s/\"//g')" \
		SmartcardIdentifier.pkg
	python3 -m pip install twine
	@echo
	@if [ ! -e ~/.pypirc ]; \
	 then echo "Please create a PyPI API token: https://pypi.org/manage/account/token/"; \
	      echo "Then save it to your ~/.pypirc file, or enter it as your PyPI password below."; \
	      echo "Press Enter to continue..."; \
	      read waiting; \
	 fi
	@python3 -m twine upload --username __token__ 'dist/*'

.PHONY: clean
clean:
	rm -rf build/ dist/
	rm -f SmartcardIdentifier.pkg

