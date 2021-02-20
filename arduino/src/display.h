#ifndef DISPLAY_H
#define DISPLAY_H

#include <Arduino.h>
#include <LiquidCrystal_PCF8574.h>

class Display
{
public:
  Display();
  ~Display();
  uint8_t init();
  void hourglass_step();
  void print(uint8_t line, String &text);
private:
  LiquidCrystal_PCF8574 *lcd;
  void find_i2c_display();
  void define_umlaut_character();
  void define_hourglass_character();
  byte hour_glass_pos;
};

#endif // DISPLAY_H
