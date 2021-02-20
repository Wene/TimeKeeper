#include <Arduino.h>
#include "display.h"
#include <MFRC522.h>

#define VERSION F("0.1.0")

#define RFID_RESET_PIN A0
#define RFID_SELECT_PIN 10
MFRC522 rfid(RFID_SELECT_PIN, RFID_RESET_PIN);

Display display;

void wait_for_host()
{
  while(true)
  {
    display.hourglass_step();
    delay(400);
  }
}

void setup()
{
  Serial.begin(115200);
  Serial.println(F("Booting TimeKeeper IO module..."));

  Serial.println(F("Searching for I2C display..."));
  uint8_t addr = display.init();
  String text = F("Booting...");
  display.print(0, text);
  Serial.print(F("Display found at address 0x"));
  Serial.println(addr, HEX);

  rfid.PCD_Init();
  Serial.println(F("RFID module initialized"));

  Serial.print(F("TimeKeeper IO module ready ("));
  Serial.print(VERSION);
  Serial.println(")");

  text = F("Waiting for horst");
  display.print(1, text);
  wait_for_host();
}

void loop()
{
}
