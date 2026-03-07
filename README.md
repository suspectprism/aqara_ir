# aqara\_ir.py

Python script to connect to Aqara APIs for access to unpublished accessories such as infra-red services.



The script connects using the official Aqara python APIs and enumerates available interfaces.

It then enumerates the IR keys for the TV virtual device and presses the Power key.


# custom_components\aqara_ir

This is a Home Assistant custom integration which is based on the successful API usage from the script. It sets up the IR TV remote virtual device as an entity in Home Assistant so that Power on/off key presses can be sent to it.
