import numpy as np
import cv2
import time
import threading
import logging

cap = cv2.VideoCapture('continuum.mp4')
fr = cap.get(cv2.cv.CV_CAP_PROP_FPS)
print 'video Frame Rate: {}'.format(fr)
base_delay = int(1000/fr)
delay = base_delay
print 'Frame delay: {}'.format(delay)




class bicyclePlayer(threading.Thread):
    def __init__(self, input_file):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('initializing {}, input file: {}'.format(self.__class__.__name__, input_file))
        super(bicyclePlayer).__init__(self)
        self.input_file = input_file
        self.video_capturer = None
        self.frame_rate = None
        self.base_delay = None  # ideal delay (1000/ frame rate)
        self.read_file()

    def read_file(self):
        self.video_capturer = cv2.VideoCapture(self.input_file)
        self.logger.info('openCV version: {}'.format(cv2.__version__))
        if cv2.__version__ > '2.4.8':
            self.frame_rate = self.video_capturer.get(cv2.CAP_PROP_FPS)
        else:
            self.frame_rate = self.video_capturer.get(cv2.cv.CV_CAP_PROP_FPS)
        self.logger.info('read frame rate: {}'.format(self.frame_rate))
        self.base_delay = int(1000 / self.frame_rate)
        self.logger.info('base delay: {}'.format(self.base_delay))

    def set_speed(self, speed):
        self.logger.debug('setting speed: {}'.format(speed))


    def run(self):
        pass



'''
frame_number = 0
stop_watch_frame = False
while(cap.isOpened()):

    if frame_number % 20 == 0:
        t0 = time.time()
        stop_watch_frame = True

    ret, frame = cap.read()

    # change frame to gray
    #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # overlay pixels [50:100, 50:100, :] with black
    overlayed = frame
    overlayed[50:100, 50:100, :] = 0

    cv2.imshow('frame', frame)

    # change play speed
    '''
    if time.time() - t0 < 20:
        delay = 10
    else:
        delay = 4
    '''
    if stop_watch_frame:
        frame_time = time.time() - t0
        print 'frame time: {}'.format(frame_time)
        delay = max(0, int(base_delay - frame_time * 1000))
        print 'frame delay: {}'.format(delay)
        stop_watch_frame = False

    if cv2.waitKey(delay) & 0xFF == ord('q'):
        break

    frame_number += 1

cap.release()
cv2.destroyAllWindows()

'''