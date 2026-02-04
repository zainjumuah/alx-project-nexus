#!/bin/bash

#This script is used to generate a strong password for my postgres, I know I will surely generate bs like the last time"
python3 - << 'PY'
import secrets
print(secrets.token_urlsafe(32))
PY
