.PHONY: install report

.DEFAULT_GOAL := report

export LC_ALL=C

install:
	sudo apt install python3-dev python3-pip libssl-dev libffi-dev gnumeric
	pip3 install -r requirements.txt

report:
	./generate-dka-report.sh
