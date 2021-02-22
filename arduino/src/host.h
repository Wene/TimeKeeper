#ifndef HOST_H
#define HOST_H

#include <Arduino.h>
#include <display.h>

class Host
{
public:
  Host(Display &display);
  void communicate(unsigned long now);

private:
  Display &display;
  void read_input();
  void request_heartbeat(unsigned long now);
  void check_heartbeat();
  void check_print();
  void indicate_host_offline(unsigned long now);

  unsigned long last_heartbeat;
  unsigned long last_hourglass;
  bool host_alive;
  bool heartbeat_requested;
  String input;
};

#endif // HOST_H
