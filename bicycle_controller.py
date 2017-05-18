import threading

import serial


class BicycleController(threading.Thread):
    OPIDS  = {'DOWN_HILL': 0,
              'UP_HILL': 1,
              'MISHOR': 2
              }

    def __init__(self, com_ports, movies, list_of_topographies):
        # initilize player
        pass

    def run(self):
        while self.alive:

            self.read_serial_data()
            # if we are not playing, change played movie
            ## button press

            # if frame number changes the load/fan state --> send data to arduino
            # set speed according to data

    def send_serial_data(self, opid):
        # 3 states of DOWN_HILL/ UP_HILL / MISHOR
        pass

    def read_serial_data(self):
        reading = True
        raw_data = []
        while reading:
            try:
                d = self._serial.read(size=1)
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



if __name__ == '__main__':
    pass
    for port_try in TestChip.TcCommunication.get_serial_ports():
        # print port_try
        ser = serial.Serial(
            port=port_try,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
    # find com ports
    # define com ports
    # start controller
