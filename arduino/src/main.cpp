#include <Arduino.h>
#include "display.h"
#include "rfid.h"

#define VERSION F("0.1.0")

Display display;
Rfid *rfid;

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

  rfid = new Rfid;
  Serial.println(F("RFID module initialized"));

  Serial.print(F("TimeKeeper IO module ready ("));
  Serial.print(VERSION);
  Serial.println(")");

  text = F("Waiting for host");
  display.print(1, text);
}

void read_serial()
{
  static String input;
  while(Serial.available())
  {
    char c = Serial.read();
    if(13 == c || 10 == c)
    {
      display.print(1, input);
      input = "";
    }
    else
    {
      input += c;
    }
  }
}

unsigned long last_time;
String card_id;

void loop()
{
  unsigned long now = millis();

  if(rfid->new_card_id(card_id))
  {
    Serial.print(F("Card ID: "));
    Serial.println(card_id);
  }

  read_serial();

  if(now > last_time + 400)
  {
    last_time = now;
    display.hourglass_step();
  }
}
