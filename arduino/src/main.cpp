#include <Arduino.h>
#include <LiquidCrystal_PCF8574.h>
#include <MFRC522.h>
#include <Wire.h>

#define NO_CHAR byte(0)
#define AUML byte(1)
#define OUML byte(2)
#define UUML byte(3)

#define VERSION F("0.1.0")

LiquidCrystal_PCF8574 *lcd;

uint8_t find_i2c_display()
{
  uint8_t found_addr = 0;
  while(0 == found_addr)  // Endless loop until a display was found - makes sure lcd is not NULL.
  {
    Wire.begin();
    for(uint8_t addr = 0; addr <= 127; addr++)
    {
      // Test I²C address
      Wire.beginTransmission(addr);
      uint8_t error = Wire.endTransmission();

      // Enable display when address was found
      if(error == 0)
      {
        found_addr = addr;
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

  return found_addr;
}

void define_umlaut_character()
{
  byte no_char[8] =
  {
    B11111,
    B10001,
    B10001,
    B10001,
    B10001,
    B10001,
    B10001,
    B11111,
  };
  lcd->createChar(NO_CHAR, no_char);

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

void setup()
{
  Serial.begin(115200);
  Serial.println(F("Booting..."));

  Serial.println(F("Searching for I2C display..."));
  uint8_t addr = find_i2c_display();
  define_umlaut_character();
  Serial.print(F("Display found at address 0x"));
  Serial.println(addr, HEX);

  Serial.print(F("Ready ("));
  Serial.print(VERSION);
  Serial.println(")");
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
  lcd->write(NO_CHAR);
  lcd->write(NO_CHAR);
  lcd->write(NO_CHAR);
}
