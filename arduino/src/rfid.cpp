#include "rfid.h"
#include <SPI.h>

Rfid::Rfid() : rfid(10, A0)
{
  SPI.begin();
  rfid.PCD_Init();
}

Rfid::Rfid(byte select_pin, byte reset_pin) : rfid(select_pin, reset_pin)
{
  SPI.begin();
  rfid.PCD_Init();
}

Rfid::~Rfid()
{
}


bool Rfid::new_card_id(String &text)
{
  bool card_present = false;

  if(rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial())
  {
    card_present = true;

    byte *data = rfid.uid.uidByte;
    byte size = rfid.uid.size;
    rfid.PICC_HaltA();

    text = "0x";
    for(byte i = 0; i < size; i++)
    {
      if(data[i] < 0x10)
      {
        text += "0";
      }
      text += String(data[i], HEX);
    }
  }

  return card_present;
}
