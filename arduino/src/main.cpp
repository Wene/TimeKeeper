#include <Arduino.h>
#include <LiquidCrystal_PCF8574.h>
#include <Wire.h>
#include <MFRC522.h>

#define VERSION F("0.1.0")

LiquidCrystal_PCF8574 *lcd;

#define RFID_RESET_PIN A0
#define RFID_SELECT_PIN 10
MFRC522 rfid(RFID_SELECT_PIN, RFID_RESET_PIN);

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
        break;
      }
    }
    Wire.end();
  }

  return found_addr;
}

#define NO_CHAR byte(0)
#define AUML byte(1)
#define OUML byte(2)
#define UUML byte(3)
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

#define HOUR_0 byte(0)
#define HOUR_1 byte(1)
#define HOUR_2 byte(2)
#define HOUR_3 byte(3)
void define_hourglass_character()
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
  lcd->createChar(HOUR_0, hour_0);

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
  lcd->createChar(HOUR_1, hour_1);

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
  lcd->createChar(HOUR_2, hour_2);

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
  lcd->createChar(HOUR_3, hour_3);
}

void wait_for_host()
{
  define_hourglass_character();

  while(true)
  {
    lcd->setCursor(15, 0);
    lcd->write(HOUR_0);
    delay(400);
    lcd->setCursor(15, 0);
    lcd->write(HOUR_1);
    delay(400);
    lcd->setCursor(15, 0);
    lcd->write(HOUR_2);
    delay(400);
    lcd->setCursor(15, 0);
    lcd->write(HOUR_3);
    delay(400);
  }
}

void setup()
{
  Serial.begin(115200);
  Serial.println(F("Booting TimeKeeper IO module..."));

  Serial.println(F("Searching for I2C display..."));
  uint8_t addr = find_i2c_display();
  lcd->setCursor(0, 0);
  lcd->print(F("Booting..."));
  Serial.print(F("Display found at address 0x"));
  Serial.println(addr, HEX);

  rfid.PCD_Init();
  Serial.println(F("RFID module initialized"));

  lcd->setCursor(0, 1);
  Serial.print(F("TimeKeeper IO module ready ("));
  Serial.print(VERSION);
  Serial.println(")");
  lcd->print(F("Waiting for host"));
  wait_for_host();

  define_umlaut_character();
}

void loop()
{
}
