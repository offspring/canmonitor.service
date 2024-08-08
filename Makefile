# -*- makefile -*-

SERVICE_NAME:=canmonitor

PYTHON_BIN:=python3
PYTHON_SYSTEM_BIN:=$(shell which $(PYTHON_BIN))

define PYTHON_RUN
	$(if $(VIRTUAL_ENV),python, $(if $(container),$(PYTHON_SYSTEM_BIN),. $(VENV_DIR)/bin/activate && python) ) $(1)
endef

PYTHON_FILES:=$(shell find * -iname '*.py' -type f)

VENV_DIR:=.venv

.PHONY: all
all: help

.PHONY: help
help: ## Show this help message.
	@echo 'usage: make [target] ...' && \
	echo && \
	echo 'targets:' && \
	perl -ne '/^(.*)\:(.*)##\ (.*)$$/ && print "$$1#$$3\n";' $(MAKEFILE_LIST) | column -t -c 2 -s '#'

.PHONY: install-requirements
install-requirements: ## Test pip install requirements.
	$(call PYTHON_RUN, -m pip install -r requirements-dev.txt -r requirements.txt)

$(VENV_DIR):
	$(PYTHON_SYSTEM_BIN) -m venv $(VENV_DIR)
	$(MAKE) install-requirements

.PHONY: venv
venv: $(VENV_DIR) ## Create venv.

.PHONY: clean
clean: ## Clean build artifacts.
	rm -rf .mypy_cache/
	rm -rf dist/
	rm -rf build_output/
	rm -rf *.egg-info
	rm -f *.log*
	rm -rf temp/

.PHONY: realclean
realclean: clean ## Clean build artifacts and delete virtual env.
	rm -rf $(VENV_DIR)/
	rm -rf dist/
	-find * -iname "*.pyc" -type f -exec rm -f {} ';'
	-find * -iname "__pycache__" -type d -exec rm -rf {} ';'
	-find * -iname "*.egg-info" -type d -exec rm -rf {} ';'

.PHONY: black
black: ## Format python code using black.
	$(call PYTHON_RUN, -m black $(PYTHON_FILES))

.PHONY: lint
lint: ## Run lint for python code.
	$(call PYTHON_RUN, -m pylint $(PYTHON_FILES))

.PHONY: mypy
mypy: ## Run mypy for python code.
	$(call PYTHON_RUN, -m mypy $(PYTHON_FILES))

install: ## Install service.
	chmod a+x ./canmonitor.py
	sudo cp ./$(SERVICE_NAME).service /etc/systemd/system/
	$(MAKE)	enable

uninstall: disable ## Uninstall service.
	-sudo rm -f /etc/systemd/system/$(SERVICE_NAME).service

enable: ## Enable service.
	sudo systemctl enable $(SERVICE_NAME).service

disable: stop ## Disable service.
	-sudo systemctl disable $(SERVICE_NAME).service

stop: ## Stop service.
	sudo systemctl stop $(SERVICE_NAME)

start: ## Start service.
	sudo systemctl start $(SERVICE_NAME)

restart: ## Restart service.
	sudo systemctl restart $(SERVICE_NAME)

status: ## Check service status.
	-sudo systemctl -l status $(SERVICE_NAME)

log: ## Tail recent log
	tail -f $(shell ls -1rt ./logs/* | tail -1) | ~/workspace/offspring/canboat/canboat/rel/linux-aarch64/analyzer

run-console: ## Run in the console
	PYTHONUNBUFFERED=1 $(call PYTHON_RUN, ./canmonitor.py) | ~/workspace/offspring/canboat/canboat/rel/linux-aarch64/analyzer

run-temp-file: ## Run in to temp file
	$(call PYTHON_RUN, ./canmonitor.py -o "$(CURDIR)/temp.log" )
