#              .';:cc;.
#            .,',;lol::c.
#            ;';lddddlclo
#            lcloxxoddodxdool:,.
#            cxdddxdodxdkOkkkkkkkd:.
#          .ldxkkOOOOkkOO000Okkxkkkkx:.
#        .lddxkkOkOOO0OOO0000Okxxxxkkkk:
#       'ooddkkkxxkO0000KK00Okxdoodxkkkko
#      .ooodxkkxxxOO000kkkO0KOxolooxkkxxkl
#      lolodxkkxxkOx,.      .lkdolodkkxxxO.
#      doloodxkkkOk           ....   .,cxO;
#      ddoodddxkkkk:         ,oxxxkOdc'..o'
#      :kdddxxxxd,  ,lolccldxxxkkOOOkkkko,
#       lOkxkkk;  :xkkkkkkkkOOO000OOkkOOk.
#        ;00Ok' 'O000OO0000000000OOOO0Od.
#         .l0l.;OOO000000OOOOOO000000x,
#            .'OKKKK00000000000000kc.
#               .:ox0KKKKKKK0kdc,.
#                      ...
#
# Author: peppe8o
# Blog: https://peppe8o.com
#
# v1.3
# date: 18th Jul, 2025

import gpiozero
from time import sleep
from gpiozero import DigitalOutputDevice
import re
import multiprocessing

# ---------------------------------------------------------------------------------------------->
# Class for passive (tonal) buzzer
# ---------------------------------------------------------------------------------------------->

class buzzer:
  def __init__(self, buzzer_PIN):
    self.duty_cycle = 0.1 # Duty cycle set to this value gives the best output quality. You can change it from 0 to 1. Duty cycle to 0 stops the buzzer
    self.b = gpiozero.PWMOutputDevice(buzzer_PIN)

  def play(self, tone, on_time = 0, off_time = 0):
    if tone == "":
       self.stop()
       return True

    self.b.value = self.duty_cycle # set the PWM duty cycle

    if isinstance(tone, int) and tone <= 127:
       self.b.frequency = gpiozero.tones.Tone.from_midi(tone) # This avoids getting a terminal warning when the input tone is probably a midi input
    else:
       self.b.frequency = gpiozero.tones.Tone(tone).frequency # Use the Tone class to get the frequency. Works with frequency, midi, and note

    if on_time > 0: sleep(on_time) # If an on_time is set, the sleep makes the buzzer playing for the corresponding number of seconds

    if off_time > 0: # if an off_time is set, the buzzer remains off for the off_time and it returns to the program after this time
       self.stop()
       sleep(off_time)

  def stop(self):
    self.b.value = 0


# --------------------------------------------------------------------------------------------------------------------------------------------
# Class for 7-segment display
# --------------------------------------------------------------------------------------------------------------------------------------------
class seven_segment:
  def __init__(self, a_PIN, b_PIN, c_PIN, d_PIN, e_PIN, f_PIN, g_PIN, dot_PIN):
    self.a = gpiozero.DigitalOutputDevice(a_PIN)
    self.b = gpiozero.DigitalOutputDevice(b_PIN)
    self.c = gpiozero.DigitalOutputDevice(c_PIN)
    self.d = gpiozero.DigitalOutputDevice(d_PIN)
    self.e = gpiozero.DigitalOutputDevice(e_PIN)
    self.f = gpiozero.DigitalOutputDevice(f_PIN)
    self.g = gpiozero.DigitalOutputDevice(g_PIN)
    self.dot = gpiozero.DigitalOutputDevice(dot_PIN)

    self.arrSeg = {\
          "0":[1,1,1,1,1,1,0],\
          "1":[0,1,1,0,0,0,0],\
          "2":[1,1,0,1,1,0,1],\
          "3":[1,1,1,1,0,0,1],\
          "4":[0,1,1,0,0,1,1],\
          "5":[1,0,1,1,0,1,1],\
          "6":[1,0,1,1,1,1,1],\
          "7":[1,1,1,0,0,0,0],\
          "8":[1,1,1,1,1,1,1],\
          "9":[1,1,1,1,0,1,1]}
    self.display_list = [self.a,self. b, self.c, self.d, self.e, self.f, self.g]

  def show(self, to_display, dotValue=False):
    value_to_display = str(to_display)

    if value_to_display not in self.arrSeg:
      raise Exception("Value not available in the seven_segment.show() dictionary")

    for i in range(0,len(self.display_list)):
      self.display_list[i].value = self.arrSeg[value_to_display][i]

    if dotValue:
      self.dot.value = 1
    else:
      self.dot.value = 0

  def clear(self):
    for i in range(0,len(self.display_list)):
      self.display_list[i].value = 0
    self.dot.value = 0



# --------------------------------------------------------------------------------------------------------------------------------------------
# Class for 4-digit 7-segment display
# --------------------------------------------------------------------------------------------------------------------------------------------

class four_digit_seven_segment:
  def __init__(self, a_PIN, b_PIN, c_PIN, d_PIN, e_PIN, f_PIN, g_PIN, dot_PIN, sel1_PIN, sel2_PIN, sel3_PIN, sel4_PIN):

    self.selectors = [gpiozero.DigitalOutputDevice(sel1_PIN),\
                      gpiozero.DigitalOutputDevice(sel2_PIN),\
                      gpiozero.DigitalOutputDevice(sel3_PIN),\
                      gpiozero.DigitalOutputDevice(sel4_PIN)]

    self.digit_display = seven_segment(a_PIN, b_PIN, c_PIN, d_PIN, e_PIN, f_PIN, g_PIN, dot_PIN)
    self.proc = multiprocessing.Process(target=self.show_4_control, args=[""])

  def show_4_control(self, to_show):
   format_matches = re.search("^\d\.?\d\.?\d\.?\d\.?", to_show) is not None

   if not format_matches:
      raise Exception("Value not matching the required format. It must be a string of 4 numbers, with optional dot (.) after each number")

   while True:
    to_display = []
    i=0
    while i < len(to_show):
      if i+1 < len(to_show) and to_show[i+1] == ".":
        to_display.append(to_show[i:i+2])
        i=i+2
      else:
        to_display.append(to_show[i])
        i=i+1

    for i in range(0,4):
      if len(to_display[i])== 2:
        dotValue = True
      else:
        dotValue = False
      for s in range(0,4): self.selectors[s].on()
      self.selectors[i].off()
      self.digit_display.show(to_display[i][0], dotValue)
      sleep(0.003)

  def show_4(self, to_show):
    if self.proc.is_alive(): self.proc.terminate()
    self.proc = multiprocessing.Process(target=self.show_4_control, args=[to_show])
    self.proc.start()

  def clear(self):
    self.proc.terminate()



# --------------------------------------------------------------------------------------------------------------------------------------------
# Class for traffic light module, using the GPIOZERO LEDBoard
# --------------------------------------------------------------------------------------------------------------------------------------------
class traffic_light:
  def __init__(self, red_LED, yellow_LED, green_LED):
    # NOTE: not well documented, however the LEDBoard seems to resort the LEDs order when assigned with a label.
    self.leds = gpiozero.LEDBoard(green = green_LED, red = red_LED, yellow = yellow_LED)

  def go(self):
    self.leds.value = (1, 0, 0) # Activates the GREEN LED and switches off all the other LEDs

  def stop(self, yellow_TIME = 3):
    self.leds.value = (1, 0, 0) # Make sure that the green LED is activated and the red LED is off 
    self.leds.yellow.blink(on_time=0.8, off_time=0.8) # Blinks the YELLOW LED for "yellow_TIME" seconds with the following sleep statement
    sleep(yellow_TIME)
    self.leds.value = (0, 1, 0) # Activates the RED LED and switches off all the other LEDs

  def off(self):
    self.leds.off() # Switches off all the LEDS
