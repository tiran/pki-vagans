IPA_PLAYBOOK=ansible/ipa-playbook.yml
PKI_PLAYBOOK=ansible/pki-playbook.yml

ANSIBLE_PLAYBOOK ?= $(shell which ansible-playbook)

.PHONY: all tags tasks check

all: check tags tasks

tags: $(ANSIBLE_PLAYBOOK)
	$(ANSIBLE_PLAYBOOK) --list-tags $(IPA_PLAYBOOK) > ipa-tags.txt
	$(ANSIBLE_PLAYBOOK) --list-tags $(PKI_PLAYBOOK) > pki-tags.txt

tasks: $(ANSIBLE_PLAYBOOK)
	$(ANSIBLE_PLAYBOOK) --list-tasks $(IPA_PLAYBOOK) > ipa-tasks.txt
	$(ANSIBLE_PLAYBOOK) --list-tasks $(PKI_PLAYBOOK) > pki-tasks.txt

check: $(ANSIBLE_PLAYBOOK)
	$(ANSIBLE_PLAYBOOK) --syntax-check $(IPA_PLAYBOOK)
	$(ANSIBLE_PLAYBOOK) --syntax-check $(PKI_PLAYBOOK)
