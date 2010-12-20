BIN_DIR = $(HOME)/bin
SCRIPTS_DIR = $(BIN_DIR)/fcrawler-scripts
SCRIPT = $(BIN_DIR)/fcrawler

.PHONY: install, uninstall, clean-install

install:
	-mkdir -vp $(BIN_DIR)
	-mkdir -vp $(SCRIPTS_DIR)
	-cp -v *.py $(SCRIPTS_DIR)
	-[ -x $(SCRIPT) ] || ln -vs $(SCRIPTS_DIR)/main.py $(SCRIPT)

uninstall:
	-rm -fv $(SCRIPTS_DIR)/*.py
	-rm -fv $(BIN_DIR)/fcrawler

clean-install: uninstall, install
