# Notes for project TimeKeeper

## Raspberry Pi

### Links
- [UART configuration](https://www.raspberrypi.org/documentation/configuration/uart.md)
- [GPIO general](https://www.raspberrypi.org/documentation/usage/gpio/)
- [Pin header schema](https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3bplus_1p0_reduced.pdf)

### Activating UART on GPIO header
Execute `raspi-config` and navigate to `3 interface options > Serial`. Here enable the UART interface but disable the default console on it. Reboot the RasPi after finishing those settings. To access the UART serial interface, the user needs to be in the groups `dialout` and `tty`.

### Test the connection
Use the command `screen /dev/ttyS0 115200` to open a screen session on the embedded UART serial interface at 115200 baud. Make sure something like an FTDI USB adaptor is connected to that interface and configured to use the same data rate. You can now type in the screen session and your input should appear on the other side and vice versa.

