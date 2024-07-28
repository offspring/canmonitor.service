
all:

install:
	chmod a+x ./canmonitor.sh
	sudo cp ./canmonitor.service /etc/systemd/system/
	sudo systemctl enable canmonitor.service

uninstall: stop
	-sudo systemctl disable canmonitor.service
	-sudo rm -f /etc/systemd/system/canmonitor.service

stop:
	sudo systemctl stop canmonitor

start:
	sudo systemctl start canmonitor

restart:
	sudo systemctl restart canmonitor

status:
	-sudo systemctl -l status canmonitor

log-create:
	sudo mkdir -p /var/log/canmonitor/

