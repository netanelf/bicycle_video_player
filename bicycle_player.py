import numpy as np
import cv2
import time
import os
import threading
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from Queue import Queue

__author__ = 'netanel'


class BicyclePlayer(threading.Thread):
    #TODO: support change of input file

    def __init__(self, overlay_debug=False):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('initializing {}'.format(self.__class__.__name__))
        super(BicyclePlayer, self).__init__()
        self.overlay_debug = overlay_debug
        self.video_capturer = None
        self.capture_thread = None
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

    def load_file(self, input_file):
        """
        load a file into the player.
        1. file and parameters (fps etc) are read
        2. frame_counter is zeroed
        3. a thread for reading the frames is constructed and started
        :param input_file:
        :return:
        """
        self.logger.info('load file called, file: {}'.format(input_file))
        self._read_file(input_file=input_file)

        if self.capture_thread is not None:
            self.capture_thread.kill_capturer()

        self.logger.info('zeroing frame counter')
        self.frame_counter = 0

        cap_thread = ThreadedCapturer(VideoCapture_obj=self.video_capturer, queue_size=100)
        cap_thread.setDaemon(True)
        cap_thread.start()
        self.capture_thread = cap_thread

    def get_frame_counter(self):
        """
        :return: return frame counter for the current file
        """
        return self.frame_counter

    def _read_file(self, input_file):
        self.video_capturer = cv2.VideoCapture(input_file)
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

        self.base_delay = 1  # TODO: changed to 1 just for now - play as quickly as we can
        self.base_delay = int(1000 / self.frame_rate)

        self.delay = self.base_delay
        self.logger.info('base delay: {}'.format(self.base_delay))

    def run(self):

        self.should_run = True
        fps_time = time.time()
        fps_frame = 0

        cv2.namedWindow('BicycleVideoWindow', cv2.WINDOW_OPENGL)
        if cv2.__version__ > '2.4.9.1':
            cv2.setWindowProperty('BicycleVideoWindow', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('BicycleVideoWindow', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

        frame_grab_time = 0
        processing_and_imshow_time = 0
        waitkey_time = 0

        while self.should_run is True:
            t0 = time.time()

            while self.paused:
                time.sleep(0.01)

            if self.capture_thread is None or self.capture_thread.q.qsize() == 0:
                time.sleep(0.01)
                continue

            frame = self.capture_thread.q.get()

            t1 = time.time()
            if frame is None:
                self.logger.info('did not receive frame, assuming file ended, jumping to start, zeroing frame_counter')
                self.video_capturer.set(cv2.cv.CV_CAP_PROP_POS_AVI_RATIO, 0)
                self.frame_counter = 0
                continue

            # copy all overlay images onto current frame
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

            # copy all overlay texts onto current frame
            if len(self.text_overlays) > 0:
                for overlay_name, overlay_data in self.text_overlays.items():
                    cv2.putText(frame, overlay_data['text'], overlay_data['location'], self.text_font, 1, (255, 255, 255), 2)

            # move frame into output buffer
            cv2.imshow('BicycleVideoWindow', frame)

            t2 = time.time()
            self.frame_counter += 1
            fps_frame += 1

            if self.frame_counter % 50 == 0:
                t = time.time()
                dt = t - fps_time
                fps = fps_frame / dt
                self.logger.debug('played {} frames in {} seconds ({} fps average)'
                                  .format(fps_frame, dt, fps))
                if self.overlay_debug:
                    self.text_overlays['debug_message'] = {'text': 'fps: {:0.2f}'.format(fps), 'location': (50, 500)}
                fps_time = t
                fps_frame = 0

            # show frame on screen
            if cv2.waitKey(self.delay) & 0xFF == ord('q'):
                break

            t3 = time.time()

            frame_grab_time += t1-t0
            processing_and_imshow_time += t2 - t1
            waitkey_time += t3 - t2

        self.video_capturer.release()
        cv2.destroyAllWindows()
        # this is the solution for window no closing (under linux?):
        # http://stackoverflow.com/questions/6116564/destroywindow-does-not-close-window-on-mac-using-python-and-opencv
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)
        cv2.waitKey(1)

        self.logger.info('playing stopped')
        self.logger.debug('timing:')
        self.logger.debug('frame_grab_time: {}'.format(frame_grab_time))
        self.logger.debug('processing_and_imshow_time: {}'.format(processing_and_imshow_time))
        self.logger.debug('waitkey_time: {}'.format(waitkey_time))

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
        ramp_speed_step = float(stop_speed - start_speed) / ramp_steps
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


class ThreadedCapturer(threading.Thread):
    """
    thread for reading frames from video file and dumping them into a Queue,
    this way the frame reading process does not block the image processing.
    """
    def __init__(self, VideoCapture_obj, queue_size):
        super(ThreadedCapturer, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.capturer = VideoCapture_obj
        self.q = Queue(maxsize=queue_size)
        self.should_run = False
        self.qsize_print_time = -1
        self.logger.info('finished initiating ThreadedCapturer')

    def run(self):
        self.logger.info('ThreadedCapturer starting')
        self.should_run = True

        while self.should_run:
            if not self.q.full():
                (grabbed, frame) = self.capturer.read()
                self.q.put(frame)

            if time.time() - self.qsize_print_time > 5:
                self.logger.debug('q size: {}'.format(self.q.qsize()))
                self.qsize_print_time = time.time()

    def kill_capturer(self):
        self.should_run = False


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
    #f = r'HD Test 1080P Full HD (Avatar).avi'
    #f = 'Jerusalem_Virtual_Ride_preview_01_140417.mp4'
    f2 = 'movie.mp4'
    f = 'movie.mp4'
    #f = 'part.mp4'
    # image = cv2.imread("mushroom.jpeg")
    player = BicyclePlayer(overlay_debug=True)
    player.setDaemon(True)
    player.start()
    player.load_file(input_file=f)
    for i in range(10):
        time.sleep(1)
        logging.info('frame: {}'.format(player.get_frame_counter()))
    player.load_file(input_file=f2)
    time.sleep(10)
    # player.overlay_image(image=image, location=[50, 50], name='icon', weight_transparency=0.5)
    #
    # player.ramp_speed(start_speed=1, stop_speed=3, ramp_time=timedelta(seconds=15))
    # player.overlay_image(image=image, location=[200, 200], name='icon2', weight_transparency=0.75)
    #
    # player.set_speed(speed=2)
    # time.sleep(10)
    # player.disable_image_overlay(name='icon')
    # player.set_speed(speed=0.5)
    # time.sleep(10)
    # player.set_speed(speed=1)
    # player.disable_image_overlay(name='icon2')
    # time.sleep(10)
    player.stop_playing()
    time.sleep(5)


