import numpy as np
import cv2
import time
import os
import threading
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta

__author__ = 'netanel'


class BicyclePlayer(threading.Thread):
    def __init__(self, input_file):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('initializing {}, input file: {}'.format(self.__class__.__name__, input_file))
        super(BicyclePlayer, self).__init__()
        self.input_file = input_file
        self.video_capturer = None
        self.frame_rate = None
        self.base_delay = None  # ideal delay (1000/ frame rate)
        self.delay = None
        self.should_run = False
        self.paused = False
        self.frame_counter = 0
        self.read_file()

    def read_file(self):
        self.video_capturer = cv2.VideoCapture(self.input_file)
        self.logger.info('openCV version: {}'.format(cv2.__version__))
        if cv2.__version__ > '2.4.9.1':
            self.frame_rate = self.video_capturer.get(cv2.CAP_PROP_FPS)
        else:
            self.frame_rate = self.video_capturer.get(cv2.cv.CV_CAP_PROP_FPS)
        self.logger.info('read frame rate: {}'.format(self.frame_rate))
        self.base_delay = int(1000 / self.frame_rate)
        self.delay = self.base_delay
        self.logger.info('base delay: {}'.format(self.base_delay))

    def run(self):
        self.should_run = True
        start_play_time = time.time()
        while(self.video_capturer.isOpened() and self.should_run is True):

            while self.paused:
                time.sleep(0.01)

            ret, frame = self.video_capturer.read()

            if frame is None:
                self.logger.info('did not receive frame, assuming file ended, jumping to start')
                self.video_capturer.set(cv2.cv.CV_CAP_PROP_POS_AVI_RATIO, 0)
                continue

            # overlay pixels [50:100, 50:100, :] with black
            overlayed = frame
            overlayed[50:100, 50:100, :] = 0

            cv2.imshow('frame', frame)
            self.frame_counter += 1
            if self.frame_counter % 200 == 0:
                t = time.time()
                dt = t - start_play_time
                self.logger.debug('played {} frames in {} seconds ({} fps average)'
                                  .format(self.frame_counter, dt, self.frame_counter / dt))
                start_play_time = t
                self.frame_counter = 0

            if cv2.waitKey(self.delay) & 0xFF == ord('q'):
                break

        self.video_capturer.release()
        cv2.destroyAllWindows()
        # this is the solution for window no closing (under linux?):
        # http://stackoverflow.com/questions/6116564/destroywindow-does-not-close-window-on-mac-using-python-and-opencv
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        self.logger.info('playing stopped')

    def set_speed(self, speed):
        self.logger.debug('set_speed was called, speed: {}'.format(speed))
        delay = int(self.base_delay * 1.0 / speed)
        if delay == 0:
            self.logger.error('speed to high')
            return
        self.delay = delay

    def get_speed(self):
        speed = self.base_delay * 1.0 / self.delay
        self.logger.info('get speed, speed: {}'.format(speed))
        return speed

    def ramp_speed(self, start_speed, stop_speed, ramp_time):
        """
        ramp up/ down speed of playing during ramp_time, beware, this function will hold the caller thread for ramp_time
        :param start_speed:
        :param stop_speed:
        :param ramp_time:
        :return:
        """
        self.logger.info('ramp_speed was called, start_speed: {}, stop_speed: {}, ramp_time: {}'
                         .format(start_speed, stop_speed, ramp_time))
        ramp_steps = int(ramp_time.total_seconds())
        ramp_time_step = ramp_time.total_seconds() / ramp_steps
        ramp_speed_step = (stop_speed - start_speed) / ramp_steps
        self.logger.debug('ramp_steps: {}, ramp_time_step: {}, ramp_speed_step: {}'
                          .format(ramp_steps, ramp_time_step, ramp_speed_step))
        for step in range(1, ramp_steps + 1):
            self.set_speed(speed=start_speed + step * ramp_speed_step)
            time.sleep(ramp_time_step)

    def stop_playing(self):
        self.logger.info('stop_play as called')
        self.should_run = False
        time.sleep(0.01)

    def pause_playing(self):
        self.logger.info('pause_playing was called')
        self.paused = not self.paused
        self.logger.debug('pause: {}'.format(self.paused))


def init_logging(logger_name, logger_level):
    logger = logging.getLogger()
    s_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(filename=os.path.join('logs', '{}_{}.log'
                                            .format(logger_name, datetime.now()
                                                    .strftime('%d-%m-%y_%H-%M-%S'))),
                                    maxBytes=10E6,
                                    backupCount=500)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logger_level)


if __name__ == '__main__':
    init_logging(logger_name='bicyclePlayer', logger_level=logging.DEBUG)
    f = 'GoPro_BMX_Bike_Riding_in_NYC_4.mp4'
    #f = 'V70309-235541.mp4'
    player = BicyclePlayer(input_file=f)
    player.setDaemon(True)
    player.start()
    time.sleep(10)
    player.ramp_speed(start_speed=3, stop_speed=0.2, ramp_time=timedelta(seconds=30))
    '''
    player.set_speed(speed=2)
    time.sleep(20)
    player.set_speed(speed=0.5)
    time.sleep(20)
    '''
    time.sleep(20)
    player.stop_playing()
    time.sleep(5)


