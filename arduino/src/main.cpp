#include <Arduino.h>
#include <LiquidCrystal_PCF8574.h>
#include <MFRC522.h>
#include <Wire.h>

#define AUML byte(0)
#define OUML byte(1)
#define UUML byte(2)

LiquidCrystal_PCF8574 *lcd;

void setup()
{
  Serial.begin(115200);
  Serial.println(F("Booting..."));

  bool searching = true;
  while(searching)
  {
    Serial.println(F("Searching for display..."));
    Wire.begin();
    for(uint8_t addr = 0; addr <= 127; addr++)
    {
      // Test I²C address
      Wire.beginTransmission(addr);
      uint8_t error = Wire.endTransmission();

      // Enable display when address was found
      if(error == 0)
      {
        searching = false;
        lcd = new LiquidCrystal_PCF8574(addr);
        lcd->begin(16, 2);
        lcd->setBacklight(255);
        lcd->clear();
        lcd->home();
        lcd->print(F("Booting..."));
        break;
      }
    }
    Wire.end();
  }
  Serial.println(F("Display found and ativated."));

  byte auml[8] =
  {
    B01010,
    B00000,
    B01110,
    B00001,
    B01111,
    B10001,
    B01111,
    B00000,
  };
  lcd->createChar(AUML, auml);

  byte ouml[8] =
  {
    B01010,
    B00000,
    B01110,
    B10001,
    B10001,
    B10001,
    B01110,
    B00000,
  };
  lcd->createChar(OUML, ouml);

  byte uuml[8] =
  {
    B01010,
    B00000,
    B10001,
    B10001,
    B10001,
    B10011,
    B01101,
    B00000,
  };
  lcd->createChar(UUML, uuml);

}


void loop()
{
  delay(500);
  lcd->clear();
  lcd->home();
  lcd->print(F("loop"));
  lcd->setCursor(0, 1);
  lcd->print("a");
  lcd->write(AUML);
  lcd->print("o");
  lcd->write(OUML);
  lcd->print("u");
  lcd->write(UUML);
}
