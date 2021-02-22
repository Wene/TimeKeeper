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
        check_print();
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
  if(heartbeat_requested)
  {
    String comp = F("heartbeat response");
    if(comp == input)
    {
      heartbeat_requested = false;
      host_alive = true;
      display.clear();
    }
  }
}

void Host::check_print()
{
  if(host_alive)
  {
    String begin = F("print "); // print 1 Hello World
    if(input.startsWith(begin))
    {
      String line_str = input.substring(begin.length(), begin.length() + 2);
      uint8_t line = line_str.toInt();
      String print_str = input.substring(begin.length() + 2);
      display.print(line, print_str);
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


