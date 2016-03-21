PLAYBOOK=ansible/playbook.yml
ANSIBLE_VENV=venv
ANSIBLE_PIP=$(ANSIBLE_VENV)/bin/pip
ANSIBLE=$(ANSIBLE_VENV)/bin/ansible
ANSIBLE_PLAYBOOK=$(ANSIBLE_VENV)/bin/ansible-playbook

.PHONY: all tags tasks check

all: check tags tasks

tags: $(ANSIBLE_PLAYBOOK)
	$(ANSIBLE_PLAYBOOK) --list-tags $(PLAYBOOK) > tags.txt

tasks: $(ANSIBLE_PLAYBOOK)
	$(ANSIBLE_PLAYBOOK) --list-tasks $(PLAYBOOK) > tasks.txt

check: $(ANSIBLE_PLAYBOOK)
	$(ANSIBLE_PLAYBOOK) --syntax-check $(PLAYBOOK)

$(ANSIBLE_PIP):
	@virtualenv --system-site-packages $(ANSIBLE_VENV)
	@$(ANSIBLE_PIP) install --upgrade pip

$(ANSIBLE): $(ANSIBLE_PIP)
	@$(ANSIBLE_PIP) install --upgrade 'ansible >= 2.0'

$(ANSIBLE_PLAYBOOK): $(ANSIBLE)

.PHONY=ansible-venv ansible-remove
ansible-venv: $(ANSIBLE)
	@echo '. $(ANSIBLE_VENV)/bin/activate'

ansible-remove:
	@rm -rf $(ANSIBLE_VENV)
