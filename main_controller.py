from threading import Thread as thread

import glob
import sys

import serial


class main_controller():

    PING = "P"

    def __init__(self):
        # create serial connection
        # create the apropriate player
        serial_found = 0
        for port_try in main_controller.get_serial_ports():
            # print port_try
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
            raise NoArduinoException()
        self.player = self.get_player()
        self.player.start()
        self.serial_reader = SerialReader(self.player,serial)
        self.serial_writer = SerialWriter(self.player, serial)
        self.serial_reader.start()
        self.serial_writer.start()
        # run all threads

        def get_player(self):
            pass

        def get_serial_ports():
            """ Lists serial port names

                :raises EnvironmentError:
                    On unsupported or unknown platforms
                :returns:
                    A list of the serial ports available on the system
            """
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
        pass

    # open vlc comnnection

    def load_movie(file):
        pass
        # implemented

    def play(self):
        pass
        # implemented

    def pause(self):
        pass
        # implemented

    def update_speed(self,new_speed):
        self.speed = new_speed

    def has_send(self):
        raise UnimplementedException()

    def do_kaftor(self,kaftor_number):
        raise UnimplementedException()


