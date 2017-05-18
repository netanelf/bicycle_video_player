from threading import Thread as thread

import glob
import sys
import serial

import generated_vlc as vlc
import os
import time

from brake_player import  BrakePlayer
from bicycle_controller import BicycleController
from bicycle_race_controller import BicycleRaceController
from history_player import HistoryPlayer


class main_controller():

    PING = "P"
    WHO_IS_COMMAND = "who_is"

    def __init__(self):
        serial_found = 0
        for port_try in self.get_serial_ports():
            self.serial = serial.Serial(
                port=port_try,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            self.serial.write(self.PING)
            if self.serial.read_all()[:1] == self.PING:
                serial_found = 1
                break
        if serial_found == 0:
            raise Exception("No Arduino detected!!")
        self.serial.write(self.WHO_IS_COMMAND)
        self.player = self.get_player()
        self.player.start()
        self.serial_reader = SerialReader(self.player, serial)
        self.serial_writer = SerialWriter(self.player, serial)
        self.serial_reader.start()
        self.serial_writer.start()
        # run all threads

        def get_player(self):
            player_type = self.serial.read(1)
            if (player_type == 0):
                return BicycleRaceController(self.serial)
            elif (player_type == 1):
                return BicycleController(self.serial)
            elif (player_type == 2):
                return BrakePlayer(self.serial)
            elif (player_type == 3):
                return

    def get_serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result

class SerialReader(thread):
    ENCODER = 0  #todo
    KAFTOR2 = 9  #todo

    def __init__(self,player, serial):
        self.player = player
        self.serial = serial

    def run(self):
        opid, data = self.read_serial()

        if opid == self.ENCODER:
            self.player.update_speed(self.calc_speed(data))

        if opid == self.KAFTOR2:
            self.player.do_kaftor(self.KAFTOR2)
            self.read_serial()


class SerialWriter(thread):

    def __init__(self,player, serial):
        self.serial = serial
        self.player = player

    def run(self):
        if self.player.has_send():
            self.serial.send(self.player.send_data)


class VlcPlayer(thread):

    def __init__(self):
        self.mp = vlc.MediaPlayer
        self.instance = self.mp.get_instance()

    def load_movie(self,file):
        self.mp.set_media(self.instance.media_new(os.path.expanduser(file)))

    def play(self):
        self.mp.play()

    def pause(self):
        self.mp.pause()

    def update_speed(self,new_speed):
        self.mp.set_rate(new_speed)

    def has_send(self):
        raise NotImplementedError()

    def do_kaftor(self,kaftor_number):
        raise NotImplementedError()


