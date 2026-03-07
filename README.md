# aqara\_ir.py

Python script to connect to Aqara APIs for access to unpublished accessories such as infra-red services.



The script connects using the official Aqara python APIs and enumerates available interfaces.

It then enumerates the IR keys for the TV virtual device and presses the Power key.

Subsequently the script will be used to build a Home Assistant plug-in so that Home Assistant automations can interact directly with infra-red Aqara accessories.

