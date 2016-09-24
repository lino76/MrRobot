ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

APP_DEPS = $(shell find vault -type f -iname '*.py')

all: server
	@echo $(ROOT_DIR)
	@echo $(APP_DEPS)

server: $(APP_DEPS) main.py compilepy
	sed "s:PATH_TOKEN:$(ROOT_DIR):" < main.py > $@
	chmod +x $@

compilepy: $(APP_DEPS)
	python3 -m compileall -f $(APP_DEPS)

