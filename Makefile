.PHONY: install report

export LC_ALL=C

install:
	pip3 install -r requirements.txt

report:
	./generate-dka-report.sh
