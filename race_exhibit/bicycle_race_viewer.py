import fnmatch
import threading
import logging
from time import sleep
import time
import numpy as np
import cv2
import os
import bicycle_race_config as cfg
from collections import defaultdict
from time import gmtime, strftime

timing_stats = defaultdict(int)


def timing_decorator(func):
    def timed_function(*args, **kwargs):
        t0 = time.clock()
        r = func(*args, **kwargs)
        t1 = time.clock()
        timing_stats[func.__name__] += (t1 - t0)
        return r

    return timed_function


class BicycleRaceViewer(threading.Thread):

    @timing_decorator
    def __init__(self, dir_name = "bicycle_race_sample_pics"):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initializing {}'.format(self.__class__.__name__))
        super(BicycleRaceViewer, self).__init__()
        self._running = False

        self._velocity = [0, 0]  # player1,player2
        self._target_velocity = [0, 0]  # player1,player2
        #self._delta = [0, 0]
        self._last_velocity_update_time = 0
        self._velocity_update_delta_kms = 0.5  # 'kamash' step for velocity updates

        self._velocity_bars = [0, 0] #self._images_structures['bar_fill']

        # hold all images (icons, background etc.)
        self._images_structures = {}
        self._read_all_images(dir_name)
        self._create_on_the_fly_images()  # create structures for graphics with no image (like velocity bar)
        self._parse_combined_digits('digits-green')
        self._parse_combined_digits('digits-yellow')
        self._parse_combined_digits('digits-white')

        # hold the image that will be displayed on screen
        self._displayed_image = None

        # Velocity bar configurations
        self._velocity_bar_min_pixel = cfg.VELOCITY_BAR_LOCATION[0][1]
        self._velocity_bar_max_pixel = cfg.VELOCITY_BAR_LOCATION[0][1] + cfg.VELOCITY_BAR_SIZE[1]
        self._velocity_bar_min_velocity = 0
        self._velocity_bar_max_velocity = 100
        self._velocity_bar_gradient_end = 0.3  # percentage of visible bar that will have a gradient effect

        self._record_date = strftime("%Y-%m-%d", gmtime())
        self._logger.info("data change {}".format(strftime("%Y-%m-%d %H:%M", gmtime())))
        self._daily_record = 0
        self._last_arduino_velocity_update_time = [0, 0]
        self._measured_arduino_intervals = [0, 0] # estimated- will be refined
        self._frame_update_duration = 0.1 # estimated- will be refined

    # reads all images under a directory into _image_structures. Name convention to key is <root after dir_name>/<filename wo extention>
    # for example if we call _read_all_images(bicycle_race_sample_pics) then bicycle_race_sample_pics/digits/0.png will
    # be stored in _images_structures['digits/0']
    @timing_decorator
    def _read_all_images(self, dir_name):
        for root, dirnames, filenames in os.walk(dir_name):
            for filename in fnmatch.filter(filenames, '*.png'):
                filename = os.path.join(root, filename)
                entryname = filename[len(dir_name) + 1:].replace('.png', '').replace('\\', '/')
                try:
                    self._images_structures[entryname] = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
                    if self._images_structures[entryname] is None:
                        raise Exception('could not find img: {}'.format(filename))
                    self._logger.info('image loaded: {}, into _image_structures with key: {}'.format(filename, entryname))
                except Exception as ex:
                    self._logger.error('could not read img: {}, ex: {}'.format(filename, ex))

        # ensure background image is fully opaque (rgb with no alpha channel)
        background = self._images_structures['Background']
        (x_dim, y_dim, z_dim) = background.shape
        self._logger.debug('background dimensions: {}'.format((x_dim, y_dim, z_dim)))
        if z_dim == 4:
            self._logger.error('background has 4 channels, removing alpha')
            self._images_structures['Background'] = background[:, :, 0:3]
            self._logger.info('new dimension: {}'.format(self._images_structures['Background'].shape))

    @timing_decorator
    def _create_on_the_fly_images(self):
        """
        this function should create graphics that do not have image files (as the velocity bar)
        :return:
        """
        self._logger.info('in _create_on_the_fly_images')
        self._logger.debug('adding struct for velocity bar 1')
        v_bar1 = np.zeros(cfg.VELOCITY_BAR_SIZE)
        v_bar1[:, :, 0] = cfg.VELOCITY_BAR_1_COLOR[0]   # R
        v_bar1[:, :, 1] = cfg.VELOCITY_BAR_1_COLOR[1]   # G
        v_bar1[:, :, 2] = cfg.VELOCITY_BAR_1_COLOR[2]   # B

        self._velocity_bars[0] = v_bar1

        self._logger.debug('adding struct for velocity bar 2')
        v_bar2 = np.zeros(cfg.VELOCITY_BAR_SIZE)
        v_bar2[:, :, 0] = cfg.VELOCITY_BAR_2_COLOR[0]   # R
        v_bar2[:, :, 1] = cfg.VELOCITY_BAR_2_COLOR[1]   # G
        v_bar2[:, :, 2] = cfg.VELOCITY_BAR_2_COLOR[2]   # G

        self._velocity_bars[1] = v_bar2

    @timing_decorator
    def _check_record(self, player_speed):
        current_date = strftime("%Y-%m-%d", gmtime())
        if self._record_date != current_date:
            self._daily_record = 0
            self._record_date = current_date
            self._logger.info("data change {}".format(current_date))
        if player_speed > self._daily_record:
            self._daily_record = player_speed
            self._logger.info("Record broke {}".format(player_speed))

    @timing_decorator
    def _parse_combined_digits(self, filename):
        self._logger.info('in _parse_combined_digits')
        combined_struct = self._images_structures['combined_digits/{}'.format(filename)]
        x_len, y_len, z_len = combined_struct.shape
        self._logger.debug('combined digits graphics length: {}'.format(y_len))

        y_separator_pixel = [0, 40, 65, 107, 147, 193, 231, 271, 310, 352, 390]

        for i in range(len(y_separator_pixel) - 1):
            digit_name = '{}/{}'.format(filename,i)
            self._images_structures[digit_name] = combined_struct[:, y_separator_pixel[i]: y_separator_pixel[i + 1], :]
            self._logger.info('added number in struct: {}'.format(digit_name))

    @timing_decorator
    def _update_velocity(self, player, new_velocity):
        """
        should be used by controller
        :param player: player1/ player2
        :param new_velocity: new velocity value
        :return:
        """
        self._logger.info('volocity updated by controller({}: {})'.format(player, new_velocity))
        self._target_velocity[player] = new_velocity
        self._measured_arduino_intervals[player] = time.time() - self._last_arduino_velocity_update_time[player]
        self._last_arduino_velocity_update_time[player] = time.time()
        self._check_record(new_velocity)

    @timing_decorator
    def _update_current_velocity(self):
        """
        update current velocity by 1 step closer to target velocity
        velocity step size: self._velocity_update_delta_kms
        :return:
        """
        # update self._velocity to next step
        for player in range(len(self._velocity)):
            next_update_time = self._last_arduino_velocity_update_time[player] + self._measured_arduino_intervals[player]
            remaining_updates = np.math.floor((next_update_time - time.time()) / self._frame_update_duration)
            speed_current_to_target = self._target_velocity[player] - self._velocity[player]
            self._velocity[player] += max(speed_current_to_target/max(remaining_updates,1),min(cfg.MIN_SPEED_STEP,speed_current_to_target))

        self._logger.debug('new velocity: {}'.format(self._velocity))

    @timing_decorator
    def _overlay(self, base_image, overlay_image, location):
        """
        overlay overlay_image on top of base_image in location location
        if overlay_image has an alpha channel, weight the overlay process with the channel
        :param base_image: ndarray (r, g, b) without alpha channel
        :param overlay_image: image to overlay
        :param location: (x, y)
        :return overlayd image
        """

        # TODO: maybe this function should go into a 'utils' file and be used also by bicycle_player
        new_image = base_image.copy()
        x_start, y_start = location
        (base_x_dim, base_y_dim, base_z_dim) = base_image.shape
        self._logger.debug('base_image dimensions: {}'.format((base_x_dim, base_y_dim, base_z_dim)))
        (x_dim, y_dim, z_dim) = overlay_image.shape
        self._logger.debug('overlay dimensions: {}'.format((x_dim, y_dim, z_dim)))

        if z_dim == base_z_dim:
            new_image[x_start: x_start + x_dim, y_start: y_start + y_dim, :] = overlay_image
            return new_image

        if z_dim == 4:  # we have an alpha channel in overlay_image
            partial_background_rgb = new_image[x_start: x_start + x_dim, y_start: y_start + y_dim, :]
            overlay_rgb = overlay_image[:, :, 0:3]
            alpha = overlay_image[:, :, 3] * 1.0 / 255  # alpha is saved as uint8
            alpha_weights = np.stack((alpha, alpha, alpha), axis=2)
            partial_background_rgb = partial_background_rgb * (1 - alpha_weights)
            weighed_overlay_rgb = overlay_rgb * alpha_weights

            new_image[x_start: x_start + x_dim, y_start: y_start + y_dim, :] = weighed_overlay_rgb + partial_background_rgb
            return new_image

    @timing_decorator
    def _change_power_state(self, speed, player):
        self._logger.debug('in _change_power_state, speed: {}, player: {}'.format(speed, player))
        for index, speed_threshold in enumerate(reversed(cfg.SPEED_STATE_THRESHOLDS)):
            if speed >= speed_threshold:
                color = 'Green' if player == 0 else 'Yellow'  # TODO: change to yello when we have more graphics
                image_name = 'states/Watt_{0}-{1:02d}'.format(color, len(cfg.SPEED_STATE_THRESHOLDS) - index)
                self._logger.debug('returned power bar image: {}'.format(image_name))
                return np.copy(self._images_structures[image_name])

    @timing_decorator
    def _update_power_bar(self):
        # according tp self.velocity:
        # update images for both players

        self._logger.debug('in _update_power_bar')
        for index in range(len(self._velocity)):
            power_state_img = self._change_power_state(self._velocity[index], index)
            self._displayed_image = self._overlay(base_image=self._displayed_image,
                                                  overlay_image=power_state_img,
                                                  location=tuple(cfg.POWER_BAR_LOCATION[index]))

            # for now, no numbers on power bar
            #digits_location = map(sum, zip(cfg.POWER_BAR_LOCATION[index], cfg.POWER_BAR_DIGIT_OFFSET))
            #self._update_number_to_screen(self._velocity[index]*cfg.SPEED_POWER_CONVERSION_FACTOR, digits_location,cfg.POWER_DIGITS_SCALING)

    @timing_decorator
    def _update_speed_placements(self):
        self._logger.debug('in _update_speed_placements')
        for index in range(len(self._velocity)):
            bar_progress_offset = [0, self._map_velocity_to_bar_location(velocity=self._velocity[index])]
            coordinates = map(sum, zip((cfg.VELOCITY_BAR_LOCATION[index][0], 0), bar_progress_offset, cfg.VELOCITY_BAR_SPEED_OFFSET))
            color = cfg.PLAYER_1_COLOR if index == cfg.PLAYER_1 else cfg.PLAYER_2_COLOR
            self._update_number_to_screen(self._velocity[index], coordinates, cfg.VELOCITY_DIGITS_SCALING, color)

    @timing_decorator
    def _update_number_to_screen(self, value, coordinates, scaling, color):
        self._logger.debug('in _update_number_to_screen')
        digits_img = self._create_number_from_digits(digit_list=self._number_to_digits(value), scaling=scaling, color=color)
        digits_offset = self._calculate_digit_offset(digits_img)
        digits_location = map(sum, zip(coordinates, digits_offset))
        self._displayed_image = self._overlay(base_image=self._displayed_image,
                                              overlay_image=digits_img,
                                              location=tuple(digits_location))

    @timing_decorator
    def _create_number_from_digits(self, digit_list, color, scaling=1):
        """
        usage example
        num = self._create_number_from_digits([3,2, 0],1)
        offset = self._calculate_digit_offset(num)
        :param digit_list:
        :param scaling:
        :return:
        """
        # paste digits one nexto another and return one image
        self._logger.debug('in _create_number_from_digits, color: {}'.format(color))
        max_h = 0
        total_w = 0
        for digit in digit_list:
            digit_img = self._images_structures["digits-{}/".format(color) + str(digit)]
            h, w = digit_img.shape[:2]
            if h > max_h:
                max_h = h
            total_w = total_w + w

        num = np.zeros((max_h, total_w, 4), np.uint8)
        last_w = 0
        for digit in digit_list:
            digit_img = self._images_structures["digits-{}/".format(color) + str(digit)]
            h, w = digit_img.shape[:2]
            num[:h, last_w:last_w + w] = digit_img
            last_w = last_w + w
            # num = cv2.cvtColor(num, cv2.COLOR_GRAY2BGR)

        if scaling != 1:
            num = cv2.resize(num, None, fx=scaling, fy=scaling, interpolation=cv2.INTER_CUBIC)

        # for result testing
        # cv2.imshow("test", num)
        # cv2.waitKey()

        return num

    # usage example
    # num = self._create_number_from_digits([3,2, 0],1)
    # offset = self._calculate_digit_offset(num)

    @timing_decorator
    def _calculate_digit_offset(self, num):
        # receives the concatenated image and returns the offset required to add in order to place its center
        h,w = num.shape[:2]
        return [-h/2, -w/2]

    @timing_decorator
    def _number_to_digits(self, number):
        self._logger.debug('in _number_to_digits')
        number = int(number)
        self._logger.debug('number: {}'.format(number))
        number_string = str(number)
        nums = []
        for ch in number_string:
            nums.append(int(ch))
        return nums

    @timing_decorator
    def _update_velocity_bar(self):
        # update records
        self._update_number_to_screen(value=self._daily_record, coordinates=cfg.RECORD_DIGIT_LOCATION, color=cfg.DAILY_RECORD_COLOR, scaling=0.5)
        # bar width + gradient
        self._update_velocity_bar_width()
        # bicycle logo placement
        self._update_bicycle_logos_placements()
        # km"sh location update
        # digits update + location
        self._update_speed_placements()

    @timing_decorator
    def _update_velocity_bar_width(self):

        for player in range(len(self._velocity)):
            bar = self._velocity_bars[player]
            location = cfg.VELOCITY_BAR_LOCATION[player]
            # create a gradual alpha mask + width mask
            bar_x, bar_y, bar_z = bar.shape
            self._logger.debug('bar shape: ({}, {}, {})'.format(bar_x, bar_y, bar_z))

            bar_stop_pixel = self._map_velocity_to_bar_location(velocity=self._velocity[player])
            self._logger.debug('bar stop pixel: {}'.format(bar_stop_pixel))
            # mask out bar from bar_stop_pixel until the end
            bar_alpha = np.ones((bar_x, bar_y), dtype=np.uint8) * 255
            bar_alpha[:, (bar_stop_pixel - cfg.VELOCITY_BAR_LOCATION[player][1]):] = 0

            self._logger.debug('bar size : {}'.format(
                (bar_stop_pixel - cfg.VELOCITY_BAR_LOCATION[player][1])))

            self._logger.debug('bar_alpha shape: {}'.format(bar_alpha.shape))
            gradient_end = int(self._velocity_bar_gradient_end * (bar_stop_pixel - cfg.VELOCITY_BAR_LOCATION[player][1]))

            for i in range(gradient_end):
                bar_alpha[:, i] = int(i*255/gradient_end)

            masked_bar = np.dstack((bar, bar_alpha))

            self._displayed_image = self._overlay(base_image=self._displayed_image, overlay_image=masked_bar, location=location)

    @timing_decorator
    def _map_velocity_to_bar_location(self, velocity):
        """
        this function should translates from velocity to the y pixel that the bar should get to,
        this will define absolute locations for bicycle icons, speed numbers, bar etc
        :param velocity:
        :return: ypixel location of and of bar
        """
        # (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min --> map one spectrum to another
        if velocity < self._velocity_bar_min_velocity:
            return self._velocity_bar_min_pixel
        if velocity > self._velocity_bar_max_velocity:
            return self._velocity_bar_max_pixel
        pixel = (velocity - self._velocity_bar_min_velocity) * (self._velocity_bar_max_pixel - self._velocity_bar_min_pixel) \
                / (self._velocity_bar_max_velocity - self._velocity_bar_min_velocity) \
                + self._velocity_bar_min_pixel
        self._logger.debug("mapping location to {}".format(pixel))
        return int(pixel)

    @timing_decorator
    def _update_bicycle_logos_placements(self):
        """
        overlay the bicycle logo on the velocity bar in the right location
        :return:
        """
        for player in range(len(self._velocity)):
            x_icon_loc = cfg.VELOCITY_BAR_LOCATION[player][0] + cfg.BICYCLE_ICON_VERTICAL_OFFSET

            y_bar_loc = self._map_velocity_to_bar_location(velocity=self._velocity[player])
            y_icon_loc = y_bar_loc + cfg.BICYCLE_ICON_HORIZONTAL_OFFSET
            self._logger.debug("y_icon_loc {}".format(y_icon_loc))
            self._displayed_image = self._overlay(base_image=self._displayed_image,
                                                  overlay_image=self._images_structures['Rider Icon'],
                                                  location=(x_icon_loc, y_icon_loc))

    @timing_decorator
    def run(self):
        self._logger.info('starting main loop')
        self._running = True
        cv2.namedWindow('display', cv2.WND_PROP_FULLSCREEN)
        #cv2.namedWindow('display', cv2.WINDOW_OPENGL)

        if cv2.__version__ > '2.4.9.1':
            cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

        image_preparation_time = 0
        imshow_time = 0
        waitkey_time = 0

        while self._running:

            # if self._target_velocity != self._velocity:
            t0 = time.clock()
            self._displayed_image = np.copy(self._images_structures['Background'])
            self._update_current_velocity()

            self._update_power_bar()

            self._update_velocity_bar()
            t1 = time.clock()
            # show image
            cv2.imshow('display', self._displayed_image)
            t2 = time.clock()

            image_preparation_time += (t1 - t0)
            imshow_time += (t2 - t1)
            #end of if

            t3 = time.clock()
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            t4 = time.clock()

            waitkey_time += t4-t3
            self._frame_update_duration = t4-t0

        self._logger.info('frame_update_duration: {}'.format(self._frame_update_duration))
        self._logger.info('image_preparation_time: {}'.format(image_preparation_time))
        self._logger.info('imshow_time: {}'.format(imshow_time))
        self._logger.info('waitkey_time: {}'.format(waitkey_time))

        self._running = False
        self._logger.info('main loop finished')

    @timing_decorator
    def stop_viewer(self):
        self._logger.info('stop_viewer was called')
        self._running = False

if __name__ == '__main__':
    from bicycle_player import init_logging
    init_logging(logger_name='BicycleRaceViewer', logger_level=logging.DEBUG)
    b = BicycleRaceViewer()
    b.setDaemon(True)
    t0 = time.clock()
    b.start()
    sleep(2)
    b._update_velocity(player=cfg.PLAYER_1, new_velocity=1)
    b._update_velocity(player=cfg.PLAYER_2, new_velocity=20)
    sleep(2)
    b._update_velocity(player=cfg.PLAYER_1, new_velocity=20)
    b._update_velocity(player=cfg.PLAYER_2, new_velocity=15)
    sleep(2)
    b._update_velocity(player=cfg.PLAYER_1, new_velocity=1)
    b._update_velocity(player=cfg.PLAYER_2, new_velocity=1)
    sleep(2)
    b._update_velocity(player=cfg.PLAYER_1, new_velocity=2)
    b._update_velocity(player=cfg.PLAYER_2, new_velocity=2)
    sleep(2)
    b.stop_viewer()
    sleep(1)

    t1 = time.clock()
    logging.info('actual time passed: {}:'.format(t1 - t0))
    logging.info('timing statistics:')
    for k in sorted(timing_stats, key=timing_stats.get, reverse=True):
        logging.info('{}: {}'.format(k, timing_stats[k]))

