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
    def __init__(self, input_file, overlay_debug=False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('initializing {}, input file: {}'.format(self.__class__.__name__, input_file))
        super(BicyclePlayer, self).__init__()
        self.overlay_debug = overlay_debug
        self.input_file = input_file
        self.video_capturer = None
        self.frame_rate = None
        self.base_delay = None  # ideal delay (1000/ frame rate)
        self.delay = None
        self.video_resolution = None
        self.should_run = False
        self.paused = False

        # image overlay placeholders
        self.image_overlays = {}

        # text overlay placeholders
        self.text_overlays = {}
        # self.overlaid_text = None
        # self.text_overlay_coordinates = None
        self.text_font = cv2.FONT_HERSHEY_SIMPLEX

        self.frame_counter = 0
        self._read_file()

    def _read_file(self):
        self.video_capturer = cv2.VideoCapture(self.input_file)
        self.logger.info('openCV version: {}'.format(cv2.__version__))
        if cv2.__version__ > '2.4.9.1':
            self.frame_rate = self.video_capturer.get(cv2.CAP_PROP_FPS)
            x_resolution = self.video_capturer.get(cv2.CAP_PROP_FRAME_WIDTH)
            y_resolution = self.video_capturer.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self.video_resolution = [x_resolution, y_resolution]
            self.logger.info('video resolution: {}'.format(self.video_resolution))
        else:
            self.frame_rate = self.video_capturer.get(cv2.cv.CV_CAP_PROP_FPS)
            x_resolution = self.video_capturer.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH)
            y_resolution = self.video_capturer.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT)
            self.video_resolution = [x_resolution, y_resolution]
            self.logger.info('video resolution: {}'.format(self.video_resolution))
        self.logger.info('read frame rate: {}'.format(self.frame_rate))
        self.base_delay = int(1000 / self.frame_rate)
        self.delay = self.base_delay
        self.logger.info('base delay: {}'.format(self.base_delay))

    def run(self):

        self.should_run = True
        start_play_time = time.time()

        cv2.namedWindow('BicycleVideoWindow', cv2.WND_PROP_FULLSCREEN)

        if cv2.__version__ > '2.4.9.1':
            cv2.setWindowProperty('BicycleVideoWindow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('BicycleVideoWindow', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)
        while (self.video_capturer.isOpened()) and (self.should_run is True):

            while self.paused:
                time.sleep(0.01)

            ret, frame = self.video_capturer.read()

            if frame is None:
                self.logger.info('did not receive frame, assuming file ended, jumping to start')
                self.video_capturer.set(cv2.cv.CV_CAP_PROP_POS_AVI_RATIO, 0)
                continue

            if len(self.image_overlays) > 0:
                for overlay_name, overlay_data in self.image_overlays.items():
                    image = overlay_data['image']
                    transparency = overlay_data['transparency']
                    x_start, y_start = overlay_data['location']
                    (x_dim, y_dim, z_dim) = image.shape
                    base_partial = frame.copy()[x_start: x_start + x_dim, y_start: y_start + y_dim, :]
                    overlaid_output = image.copy()
                    cv2.addWeighted(image, transparency, base_partial, 1 - transparency, 0, overlaid_output)
                    frame[x_start: x_start + x_dim, y_start: y_start + y_dim, :] = overlaid_output

            if len(self.text_overlays) > 0:
                for overlay_name, overlay_data in self.text_overlays.items():
                    cv2.putText(frame, overlay_data['text'], overlay_data['location'], self.text_font, 1, (255, 255, 255), 2)

            cv2.imshow('BicycleVideoWindow', frame)
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
        """
        set playing speed
        :param speed: new speed, 1: normal speed 0.5: 50% etc.
        :return:
        """
        self.logger.debug('set_speed was called, speed: {}'.format(speed))
        delay = int(self.base_delay * 1.0 / speed)
        if delay == 0:
            self.logger.error('speed to high')
            return

        if self.overlay_debug:
            self.text_overlays['debug_message'] = {'text': 'speed: {}'.format(speed), 'location': (50, 500)}

        self.delay = delay

    def get_speed(self):
        """
        :return: current playing speed
        """
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
            s = start_speed + step * ramp_speed_step
            self.set_speed(speed=s)
            time.sleep(ramp_time_step)

    def stop_playing(self):
        """
        stop playing, object is killed
        :return:
        """
        self.logger.info('stop_play as called')
        self.should_run = False
        time.sleep(0.01)

    def pause_playing(self):
        """
        toggle pause
        :return:
        """
        self.logger.info('pause_playing was called')
        self.paused = not self.paused
        self.logger.debug('pause: {}'.format(self.paused))

    def overlay_image(self, image, location, name, weight_transparency=1):
        """
        overlay the given image in some location from now until a newer image is given or disable_overlay is called.
        :param image: n*m*3 image rgb matrix (numpy.ndarray)
        :param location: [x, y]
        :param name: name for this overlay - so we can remove this overlay when we want
        :param weight_transparency: 0 - overlaid image is transparent, 1: opaque
        :return:
        """
        self.logger.info('overlay_image was called')

        # TODO: here we should check matrix dimensions, etc.
        (x_dim, y_dim, z_dim) = image.shape
        [video_x, video_y] = self.video_resolution
        if x_dim + location[0] > video_x or y_dim + location[1] > video_y:
            self.logger.error('overlaid image to big: {}, (video size: {})'.format(image.shape, self.video_resolution))
            return

        self.image_overlays[name] = {'image': image, 'location': location, 'transparency': weight_transparency}
        self.logger.debug('created overlay image with dimensions: {}'.format(self.image_overlays[name]['image'].shape))

    def disable_image_overlay(self, name):
        self.logger.info('disable_overlay was called, name: {}'.format(name))
        self.image_overlays.pop(name)

    def overlay_text(self, text, location, name):
        """
        overlay text
        :param text: the wanted text
        :param location: (x, y) ccordinates
        :param name: name of this overlay so we can remove it later
        :return:
        """
        self.text_overlays[name] = {'text': text, 'location': tuple(location)}

    def disable_text_overlay(self, name):
        self.text_overlays.pop(name)

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
    f = 'movie.mp4'
    image = cv2.imread("icon.png")
    player = BicyclePlayer(input_file=f, overlay_debug=True)
    player.setDaemon(True)
    player.start()
    time.sleep(10)
    player.overlay_image(image=image, location=[50, 50], name='icon',weight_transparency=0.5)

    player.ramp_speed(start_speed=3, stop_speed=0.2, ramp_time=timedelta(seconds=15))
    player.overlay_image(image=image, location=[200, 200], name='icon2', weight_transparency=0.75)

    player.set_speed(speed=2)
    time.sleep(10)
    player.disable_image_overlay(name='icon')
    player.set_speed(speed=0.5)
    time.sleep(10)
    player.set_speed(speed=1)
    player.disable_image_overlay(name='icon2')
    time.sleep(10)
    player.stop_playing()
    time.sleep(5)


