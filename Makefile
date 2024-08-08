
SERVICE_NAME:=canmonitor

all:

install:
	chmod a+x ./canmonitor.py
	sudo cp ./$(SERVICE_NAME).service /etc/systemd/system/
	$(MAKE)	enable

uninstall: disable
	-sudo rm -f /etc/systemd/system/$(SERVICE_NAME).service

enable:
	sudo systemctl enable $(SERVICE_NAME).service

disable: stop
	-sudo systemctl disable $(SERVICE_NAME).service

stop:
	sudo systemctl stop $(SERVICE_NAME)

start:
	sudo systemctl start $(SERVICE_NAME)

restart:
	sudo systemctl restart $(SERVICE_NAME)

status:
	-sudo systemctl -l status $(SERVICE_NAME)

log:
	tail -f $(shell ls -1rt ./logs/* | tail -1)  | ~/workspace/offspring/canboat/canboat/rel/linux-aarch64/analyzer

test:
	tail -f $(shell ls -1rt ./logs/* | tail -1)  | ~/workspace/offspring/canboat/canboat/rel/linux-aarch64/analyzer
