PLAYBOOK=ansible/playbook.yml

.PHONY: all tags tasks check

all: check tags tasks

tags:
	ansible-playbook --list-tags $(PLAYBOOK) > tags.txt

tasks:
	ansible-playbook --list-tasks $(PLAYBOOK) > tasks.txt

check:
	ansible-playbook --syntax-check $(PLAYBOOK)

