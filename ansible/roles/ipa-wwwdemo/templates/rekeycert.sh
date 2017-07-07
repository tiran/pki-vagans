#!/bin/bash
set -ex

ipa-getcert rekey -w -f {{ cert }}
