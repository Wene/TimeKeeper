#include "display.h"
#include <Wire.h>


Display::Display()
{
  hour_glass_pos = 0;
}

Display::~Display()
{
  if(lcd)
  {
    delete lcd;
  }
}

uint8_t Display::init()
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
        break;
      }
    }
    Wire.end();
  }

  define_hourglass_character();
  define_umlaut_character();

  return found_addr;
}

void Display::print(uint8_t line, String &text)
{
  lcd->setCursor(0, line);
  // TODO: replace umlauts in text
  lcd->print(text);
}

void Display::hourglass_step()
{
  lcd->setCursor(15, 0);
  lcd->write(hour_glass_pos);
  hour_glass_pos++;
  if(hour_glass_pos > 3)
  {
    hour_glass_pos = 0;
  }
}

#define NO_CHAR byte(4)
#define AUML byte(5)
#define OUML byte(6)
#define UUML byte(7)
void Display::define_umlaut_character()
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

void Display::define_hourglass_character()
{
  byte hour_0[8] =
  {
    B11111,
    B11111,
    B11111,
    B01110,
    B01010,
    B10001,
    B10001,
    B11111,
  };
  lcd->createChar(0, hour_0);

  byte hour_1[8] =
  {
    B11111,
    B10001,
    B11111,
    B01110,
    B01010,
    B10001,
    B11111,
    B11111,
  };
  lcd->createChar(1, hour_1);

  byte hour_2[8] =
  {
    B11111,
    B10001,
    B10001,
    B01110,
    B01010,
    B11111,
    B11111,
    B11111,
  };
  lcd->createChar(2, hour_2);

  byte hour_3[8] =
  {
    B11111,
    B10001,
    B10001,
    B01010,
    B01110,
    B11111,
    B11111,
    B11111,
  };
  lcd->createChar(3, hour_3);
}
