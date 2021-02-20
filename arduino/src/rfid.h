#ifndef RFID_H
#define RFID_H

#include <Arduino.h>
#include <MFRC522.h>

class Rfid
{
public:
  Rfid();
  Rfid(byte select_pin, byte reset_pin);
  ~Rfid();
  bool new_card_id(String &text);
private:
  MFRC522 *rfid;
};

#endif // RFID_H
