from threading import Thread as thread
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import glob
import sys
import serial

import generated_vlc as vlc
import os
import time

#from brake_player import  BrakePlayer
#from bicycle_controller import BicycleController
#from bicycle_race_controller import BicycleRaceController
#from history_player import HistoryPlayer


class main_controller():

    PING = "P\n"
    WHO_IS_COMMAND = "who_is\n"
    IDENTIFICATION_OP_ID = '5'

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initiating main_controller')
        serial_found = 0
        ports = self.get_serial_ports()
        
        self.serial_connections = {}  # player_number: serial_conn
        for port_try in ports:
            s = serial.Serial(
                port=port_try,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=2
            )
            s.flush()
            s.write(self.PING)
            time.sleep(1)
            if self.PING.strip() in s.read_all().split('\n'):
                (self.player, player_number) = self.get_player(s)
                self.player.setDaemon(True)
                self.player.start()
                self.serial_connections[player_number] = s
                
        if len(self.serial_connections) == 0:
            raise Exception("No Arduino detected!!")
        
        self.serial_reader = SerialReader(self.player, self.serial_connections)
        self.serial_writer = SerialWriter(self.player, self.serial_connections)
        self.serial_reader.setDaemon(True)
        self.serial_writer.setDaemon(True)
        self.serial_reader.start()
        self.serial_writer.start()

    def get_player(self, serial_conn):
        print 'in get_player'
        serial_conn.write(self.WHO_IS_COMMAND)
        time.sleep(1)
        data = serial_conn.read_all().split('\n')
        print data
        for d in data:
            print d
            if len(d) > 0 and d[0] == self.IDENTIFICATION_OP_ID:
                player_type = int(d[1])
                player_number = int(d[2])
                print 'found player: {}, number: {}'.format(player_type, player_number)

        if (player_type == 0):
            return (BicycleRaceController(), player_number)
        elif (player_type == 1):
            return (BicycleController(), player_number)
        elif (player_type == 2):
            return (BrakePlayer(), player_number)
        elif (player_type == 3):
            from bicycle_race_controller import BicycleRaceController 
            return (BicycleRaceController(), player_number)
        else:
            raise Exception('could not get identification from arduino')

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
                print 'testing port: {}'.format(port)
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
            except Exception as ex:
                print 'got exception: {}'.format(ex)
        return result

class SerialReader(thread):
    ENCODER = 0  #todo
    KAFTOR2 = 9  #todo

    def __init__(self,player, serial_connections):
        self._logger = logging.getLogger(self.__class__.__name__)
        super(SerialReader, self).__init__()
        self.player = player
        self.serial_connections = serial_connections

    def run(self):
        while 1:
            for (id, connection) in self.serial_connections.items():
                opid, data = self.read_serial_data(serial_conn=connection)

                if opid == self.ENCODER:
                    encoder_delta = int(''.join(data))
                    self.player.update_encoder(id, encoder_delta)

                if opid == self.KAFTOR2:
                    self.player.do_kaftor(self.KAFTOR2)
                    self.read_serial()
    
    def read_serial_data(self, serial_conn):
        reading = True
        raw_data = []
        while reading:
            try:
                d = serial_conn.read(size=1)
                if d == '\n':
                    reading = False
                elif d != '':
                    raw_data.append(d)

            except Exception as ex:
                self._logger.error(ex)

        self._logger.debug(raw_data)

        op_id = int(raw_data[0])
        data = raw_data[1:]
        self._logger.debug('op_id: {}, data: {}'.format(op_id, data))

        return (op_id, data)

class SerialWriter(thread):

    def __init__(self,player, serial):
        super(SerialWriter, self).__init__()
        self.serial = serial
        self.player = player

    def run(self):
        while(1):
            time.sleep(1)
        #if self.player.has_send():
        #    self.serial.send(self.player.send_data)


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


def init_logging(log_name, logger_level):
    logger = logging.getLogger()
    s_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(filename=os.path.join('logs', '{}_{}.log'
                                            .format(log_name, datetime.now()
                                                    .strftime('%d-%m-%y_%H-%M-%S'))),
                                    maxBytes=10E6,
                                    backupCount=500)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logger_level)


if __name__ =='__main__':
    init_logging(log_name='main_controller', logger_level=logging.INFO)
    m = main_controller()
    while m.player.is_alive():
        time.sleep(1)
