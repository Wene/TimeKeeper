# TimeKeeper

## Project Goal

An open source, simple, and cheap solution for work time collection.

## Components

Every TimeKeeper collection point is equipped with a Raspberry Pi and some electronic components for RFID communication. In the only so far implemented version, those are a display and an RFID reader for the communication with the users and an Arduino to abstract the communication between the other electronic components and the Raspberry Pi. (See the schematics below)

Then, there is a desktop software written in Python using the PyQt libraries to view and manage the data. It's quite minimal at the moment. But as usage grows, the desktop client should be able to grow as well.

### Arduino Abstraction

The abstraction over the Arduino was chosen because there are some well established libraries available to interface with the display and the RFID reader. Of course, on the Raspberry Pi there are also libraries available to communicate directly with those components. But those aren't part of the main OS distribution. So on every update, we would have to take care to maintain compatibility. And since the Raspberrys are connected to the network, keeping them up to date is highly recommended. The serial interface used to communicate to the Arduino is part of the main distribution. On the other hand, the Arduino is not connected to the network and therefore less susceptible to attacks. And those libraries are way better integrated and available for a wide range of components in Arduino and PlatformIO. So in the future it should be simple to extend the system by other display and RFID reader types by just small changes in the PlatformIO code.

## Schematics

```
                  ┌───────────────────────────────────────────────────┐
                  │                                                   │
                  │            ┌──────────────────────────────────────┼──┐
                  │            │                                      │  │
┌─────────────────┴────────┐   │              ┌──────────────────┐    │  │
│                          │   │              │                  │    │  │
│                3v3   5v0 │   │              │ Arduino          │    │  │
│                          │   │              │ Pro Mini         │    │  │
│                      5v0 │   │              │ 328P 3v3 8 MHz   │    │  │
│   Raspberry Pi           │   │              │                  │    │  │
│                      GND ├───┘        ┌─────┤ TX               │    │  │
│                          │            │     │                  │    │  │
│                      TXD ├────────────┼─────┤ RX           GND ├────┼──┤
│                          │            │     │                  │    │  │
│                      RXD ├────────────┘     │                  │    │  │
│                          │                  │                  │    │  │
│                          │                  │              VCC ├────┤  │
└──────────────────────────┘                  │                  │    │  │
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
