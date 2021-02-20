#include <Arduino.h>
#include "display.h"
#include "rfid.h"

#define VERSION F("0.1.0")

Display display;

void wait_for_host(Rfid &rfid)
{
  String card_id;
  while(true)
  {
    display.hourglass_step();
    delay(400);
    if(rfid.new_card_id(card_id))
    {
      Serial.print(F("New Card ID: "));
      Serial.println(card_id);
      display.print(1, card_id);
    }
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

  Serial.println(F("RFID module initialized"));

  Serial.print(F("TimeKeeper IO module ready ("));
  Serial.print(VERSION);
  Serial.println(")");

  text = F("Waiting for host");
  display.print(1, text);
  Rfid rfid;
  wait_for_host(rfid);
}

void loop()
{
}
