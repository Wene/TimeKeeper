# Notes for project TimeKeeper

## Raspberry Pi

### Links
- [UART configuration](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-uarts)
- [GPIO general](https://www.raspberrypi.com/documentation/computers/os.html#gpio-and-the-40-pin-header)
- [Pin header schema](https://www.raspberrypi.org/documentation/hardware/raspberrypi/schematics/rpi_SCH_3bplus_1p0_reduced.pdf)

### Activating UART on GPIO header
Execute `raspi-config` and navigate to `3 interface options > Serial`. Here enable the UART interface but disable the default console on it. Reboot the RasPi after finishing those settings. To access the UART serial interface, the user needs to be in the groups `dialout` and `tty`.

### Test the connection
Use the command `screen /dev/ttyS0 115200` to open a screen session on the embedded UART serial interface at 115200 baud. Make sure something like an FTDI USB adapter is connected to that interface and configured to use the same data rate. You can now type in the screen session and your input should appear on the other side and vice versa.




```

                  ┌───────────────────────────────────────────────────┐
                  │                                                   │
┌─────────────────┴────────┐                                          │
│                          │                                          │
│                3v3   5v0 │                                          │
│                          │                                          │
│                      5v0 │                                          │
│   Raspberry Pi           │                                          │
│                      GND ├──────────────────────────────────────────┼──┐
│                          │                                          │  │
│                      TXD ├─────────┐        ┌──────────────────┐    │  │
│                          │         │        │                  │    │  │
│                      RXD ├─────────┼──┐     │ Arduino          │    │  │
│                          │         │  │     │ Pro Mini         │    │  │
│                          │         │  │     │ 328P 3v3 8 MHz   │    │  │
└──────────────────────────┘         │  │     │                  │    │  │
                                     │  └─────┤ TX               │    │  │
                                     │        │                  │    │  │
                                     └────────┤ RX           GND ├────┼──┤
                                              │                  │    │  │
                                              │                  │    │  │
                                              │                  │    │  │
                                              │              VCC ├────┤  │
                                              │                  │    │  │
                                              │                  │    │  │                      ┌───────────────────────┐
                                        ┌─────┼─── A5 (SCL)      │    │  │                      │                       │
┌─────────────────────────────┐         │     │               10 ├────┼──┼──────────────────────┤ SDA                   │
│                             │         │  ┌──┼─── A4 (SDA)      │    │  │                      │                       │
│                         GND ├──────┐  │  │  │               11 ├────┼──┼───────────────┐  ┌───┤ SCK                   │
│                             │      │  │  │  │                  │    │  │               │  │   │                       │
│                         VCC ├───┐  │  │  │  │               12 ├────┼──┼────────────┐  └──┼───┤ MOSI                  │
│ Display (3V3 tolerant)      │   │  │  │  │  │                  │    │  │            │     │   │                       │
│                         SDA ├───┼──┼──┼──┘  │               13 ├────┼──┼─────────┐  └─────┼───┤ MISO                  │
│                             │   │  │  │     │                  │    │  │         │        │   │           RFID-RC522  │
│                         SCL ├───┼──┼──┘     │               A0 ├────┼──┼──────┐  └────────┘   │ IRQ                   │
│                             │   │  │        │                  │    │  │      │               │                       │
└─────────────────────────────┘   │  │        └──────────────────┘    │  ├──────┼───────────────┤ GND                   │
                                  │  │                                │  │      │               │                       │
                                  │  └────────────────────────────────┼──┘      └───────────────┤ RST                   │
                                  │                                   │                         │                       │
                                  └───────────────────────────────────┴─────────────────────────┤ 3v3                   │
                                                                                                │                       │
                                                                                                └───────────────────────┘

```
