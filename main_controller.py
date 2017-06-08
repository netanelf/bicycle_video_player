import glob
import logging
import os
import serial
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
from threading import Thread as thread
import Queue
import generated_vlc as vlc
#from history_exhibit.history_controller import HistoryController


class main_controller():

    PING = "P\n"
    WHO_IS_COMMAND = "who_is\n"
    IDENTIFICATION_OP_ID = '5'

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initiating main_controller')
        serial_found = 0
        ports = self.get_serial_ports()
        
        self.player = None
        self.serial_reader = {}
        self.serial_writer = {}
        self.serial_connections = {}  # player_number: serial_conn
        for port_try in ports:
            print port_try
            s = serial.Serial(
                port=port_try,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=2
            )
            s.flush()
            time.sleep(2)
            s.write(self.PING)
            time.sleep(2)
            response = s.read_all().split('\n')
            print response
            if self.PING.strip() in response:
                print port_try
                (player, player_number) = self.get_player(s)
                if not self.player:
                    self.player = player             
                    self.player.setDaemon(True)
                    self.player.start()
                self.serial_connections[player_number] = s
                
        if len(self.serial_connections) == 0:
            raise Exception("No Arduino detected!!")
        
        for (conn_id, connection) in self.serial_connections.items():
            self.serial_reader[conn_id] = SerialReader(self.player, conn_id, connection)
            self.serial_writer[conn_id] = SerialWriter(self.player, conn_id, connection)
            self.serial_reader[conn_id] .setDaemon(True)
            self.serial_writer[conn_id] .setDaemon(True)
            self.serial_reader[conn_id] .start()
            self.serial_writer[conn_id] .start()

    def get_player(self, serial_conn):
        print 'in get_player'
        serial_conn.flush()
        time.sleep(2)
        serial_conn.write(self.WHO_IS_COMMAND)
        time.sleep(2)
        data = serial_conn.read_all().split('\n')
        print data
        for d in data:
            print d
            if len(d) > 0 and d[0] == self.IDENTIFICATION_OP_ID:
                player_type = int(d[1])
                player_number = int(d[2])
                print 'found player: {}, number: {}'.format(player_type, player_number)

        if (player_type == 1):
            from history_exhibit.history_controller import HistoryController
            return (HistoryController(), player_number)
        elif (player_type == 2):
            from tour_exhibit.tour_controller import TourController
            return (TourController(player_number=player_number), player_number)
        elif (player_type == 3):
            from brake_exhibit.brake_controller import BrakeController
            return (BrakeController(), player_number)
        elif (player_type == 4):
            from race_exhibit.race_controller import RaceController
            return (RaceController(), player_number)
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
            except (OSError, serial.SerialException) as ex:
                print 'got exception: {}'.format(ex)
            except Exception as ex:
                print 'got exception: {}'.format(ex)
        return result


class SerialReader(thread):
    ENCODER = 0  #todo
    KAFTOR2 = 9  #todo

    def __init__(self,player, conn_id, serial_connection):
        self._logger = logging.getLogger(self.__class__.__name__)
        super(SerialReader, self).__init__()
        self.player = player
        self.conn_id = conn_id
        self.serial_connection = serial_connection
        self.serial_connection.flush()
        self._logger.info('initialized SerialReader')

    def run(self):
        while 1:
            opid, data = self.read_serial_data(serial_conn=self.serial_connection)

            if opid == self.ENCODER:
                encoder_delta = int(''.join(data))
                self.player.update_encoder(self.conn_id, encoder_delta)

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

    def __init__(self, player, id, serial):
        super(SerialWriter, self).__init__()
        self._logger = logging.getLogger(self.__class__.__name__)
        self.serial = serial
        self.player = player
        self._logger.info('initialized SerialWriter')

    def run(self):
        while True:
            time.sleep(1)
            d = self.player.data_to_send.get()
            self._logger.debug('got data to send: {}'.format(d))
            self.serial.write(d + '\n')


class VlcPlayer(thread):

    def __init__(self, num_of_mps=1):
        super(VlcPlayer, self).__init__()
        self.mp = vlc.MediaPlayer()
        self.instance = self.mp.get_instance()
        self.data_to_send = Queue.Queue()

    def load_movie(self,file,media_sel=0):
        self.mp.set_media(self.instance.media_new(os.path.expanduser(file)))

    def play(self,media_sel=0):
        self.mp.play()

    def pause(self,media_sel=0):
        self.mp.pause()

    def update_speed(self,new_speed,media_sel=0):
        self.mp.set_rate(new_speed)

    def get_time(self):
        """
        get time in movie
        @return: time [mS]
        """
        return self.mp.get_time()

    def gradual_speed_change(self, steps):
        """
        change the play speed gradually, steps should be in the format:
        [('dwell time', 'speed'), (0.4[S], 0.9xNormal)]

         ie:
         SPEED_UP_RAMPING = [
            (0.5, 0.3),
            (0.5, 0.7),
            (0.5, 0.9),
            ]
        :param steps:
        :return:
        """
        for (delta_t, speed) in steps:
            self._logger.debug('setting speed = {}'.format(speed))
            self.update_speed(new_speed=speed)
            time.sleep(delta_t)

    def do_kaftor(self,kaftor_number):
        raise NotImplementedError()

    def update_encoder(self, player_id, encoder_data):
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
    init_logging(log_name='main_controller', logger_level=logging.DEBUG)
    m = main_controller()
    while m.player.is_alive():
        time.sleep(1)
