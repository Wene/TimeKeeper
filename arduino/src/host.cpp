#include "host.h"

Host::Host(Display &display) : display{display}
{
  host_alive = false;
}

void Host::communicate(unsigned long now)
{
  read_input();
  request_heartbeat(now);
  if(!host_alive)
  {
    indicate_host_offline(now);
  }
}

void Host::read_input()
{
  while(Serial.available())
  {
    char c = Serial.read();
    if(13 == c || 10 == c)
    {
      if(input.length() > 0)
      {
        check_heartbeat();
        input = "";
      }
    }
    else
    {
      if(input.length() < 80)
      {
        input += c;
      }
    }
  }
}

void Host::request_heartbeat(unsigned long now)
{
  if(now > last_heartbeat + 5000)
  {
    last_heartbeat = now;

    if(heartbeat_requested)
    {
      if(host_alive)
      {
        String text = F("Reconnecting...");
        display.print(0, text);
        text = F("Host connection");
        display.print(1, text);
        host_alive = false;
      }
    }
    Serial.println(F("heartbeat request"));
    heartbeat_requested = true;
  }
}

void Host::check_heartbeat()
{
  String comp = F("heartbeat response");
  if(comp == input)
  {
    if(heartbeat_requested)
    {
      heartbeat_requested = false;
      host_alive = true;
      display.clear();
    }
  }
}

void Host::indicate_host_offline(unsigned long now)
{
  if(now > last_hourglass + 400)
  {
    last_hourglass = now;
    display.hourglass_step();
  }
}


