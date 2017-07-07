#!/bin/bash
set -e

rm -f {{ private_key }} {{ cert }}
ipa-getcert stop-tracking
    -k {{ private_key }} \
    -f {{ cert }}
