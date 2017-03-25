import threading
import logging
from time import sleep
import time
from os import path
import numpy as np
import cv2


class BicycleRaceViewer(threading.Thread):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initializing {}'.format(self.__class__.__name__))
        super(BicycleRaceViewer, self).__init__()
        self._running = False

        self._velocity = {'player1': 0.1, 'player2': 0.1}
        self._target_velocity = {'player1': 0, 'player2': 0}
        self._last_velocity_update_time = 0
        self._velocity_update_delay_sec = 0.03  # update velocity resolution
        self._velocity_update_delta_kms = 0.4  # 'kamash' step for velocity updates

        # images decelerations
        self._base_image_dir = 'bicycle_race_sample_pics'

        self.background_img = path.join(self._base_image_dir, 'background.png')
        self.velocity_bicycle_icon_img = path.join(self._base_image_dir, 'bicycle_icon.png')
        self.velocity_bar_player_1_img = path.join(self._base_image_dir, 'bar_fill.png')
        self.velocity_bar_player_2_img = path.join(self._base_image_dir, 'bar_fill.png')
        self.other_img = path.join(self._base_image_dir, '1')  # demo of un-found image

        # hold all images (icons, background etc.)
        self._images_structures = {}

        self._read_all_images()

        # hold the image that will be displayed on screen
        self._displayed_image = None

        # Velocity bar configurations
        self._player_1_bicycle_icon_x = 150
        self._player_2_bicycle_icon_x = 300
        self._velocity_bar_min_pixel = 100
        self._velocity_bar_max_pixel = 1200
        self._velocity_bar_min_velocity = 0
        self._velocity_bar_max_velocity = 100
        self._velocity_bar_bicycle_icon_offset = -50  # ofset of bicycle icon from bar end
        self._velocity_bar_player_1_location = (100, 50)
        self._velocity_bar_player_2_location = (300, 50)
        self._velocity_bar_gradient_steps = 30  # number of different opacity values in the gradient
        self._velocity_bar_gradient_end = 0.3  # percentage of visible bar that will have a gradient effect

    def _read_all_images(self):
        """
        read all variables that have '_img' in their name into a dictionary (self.images_structures)
        that will hold the actual images matrices
        :return:
        """
        self._logger.info('in _read_all_images')
        self._logger.info('openCV version: {}'.format(cv2.__version__))

        images_names_vars = [v for v in vars(self) if '_img' in v]
        self._logger.debug('read variable: {}'.format(images_names_vars))

        for img_name in images_names_vars:
            try:
                self._images_structures[img_name] = cv2.imread(getattr(self, img_name), cv2.IMREAD_UNCHANGED)
                if self._images_structures[img_name] is None:
                    raise Exception('could not find img: {}'.format(img_name))

            except Exception as ex:
                self._logger.error('could not read img: {}, ex: {}'.format(img_name, ex))

        # ensure background image is fully opaque (rgb with no alpha channel)
        background = self._images_structures['background_img']
        (x_dim, y_dim, z_dim) = background.shape
        self._logger.debug('background_img dimensions: {}'.format((x_dim, y_dim, z_dim)))
        if z_dim == 4:
            self._logger.error('background_img has 4 channels, removing alpha')
            self._images_structures['background_img'] = background[:, :, 0:3]
            self._logger.info('new dimension: {}'.format(self._images_structures['background_img'].shape))

        self._logger.info('finished reading all images into cv objects')

    def update_velocity(self, player, new_velocity):
        """
        should be used by controller
        :param player: player1/ player2
        :param new_velocity: new velocity value
        :return:
        """
        self._logger.info('volocity updated by controller({}: {})'.format(player, new_velocity))
        self._target_velocity[player] = new_velocity

    def _update_current_velocity(self):
        """
        update current velocity by 1 step closer to target velocity
        velocity step size: self._velocity_update_delta_kms
        update delta time: self._velocity_update_delay_sec
        :return:
        """
        # update self._velocity to next step
        if time.time() - self._last_velocity_update_time > self._velocity_update_delay_sec:
            for (player, velocity), (player, target_velocity) in zip(self._velocity.items(), self._target_velocity.items()):
                if target_velocity > velocity:
                    self._velocity[player] = min(velocity + self._velocity_update_delta_kms, target_velocity)
                else:
                    self._velocity[player] = max(velocity - self._velocity_update_delta_kms, target_velocity)

            self._logger.debug('new velocity: {}'.format(self._velocity))
            self._last_velocity_update_time = time.time()

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

    def _update_power_bar(self):
        # according tp self.velocity:
        # update images for both players
        self._logger.debug('in _update_power_bar')
        self._update_power_bar_digits()

    def _update_power_bar_digits(self):
        # according to self.velocity:
        # update images for both players ()

        # if power > 100 change image location - ensure digits center
        pass

    def _create_number_from_digits(self, digit_list):
        # paste digits one nexto another and return one image
        return

    def _calculate_digit_offset(self, digit_list):
        # calculate horizontal offset according to number of digits and digit width
        return

    def _update_velocity_bar(self):
        # bar width + gradient
        self._update_velocity_bar_width()
        # bicycle logo placement
        self._update_bicycle_logos_placements()
        # km"sh location update
        # digits update + location

    def _update_velocity_bar_width(self):

        for player, velocity in self._velocity.items():
            if player == 'player1':
                bar = self._images_structures['velocity_bar_player_1_img']
                location = self._velocity_bar_player_1_location
            else:
                bar = self._images_structures['velocity_bar_player_2_img']
                location = self._velocity_bar_player_2_location

            # create a gradual alpha mask + width mask
            bar_x, bar_y, bar_z = bar.shape
            self._logger.debug('bar shape: ({}, {}, {})'.format(bar_x, bar_y, bar_z))

            bar_stop_pixel = self._map_velocity_to_bar_location(velocity=velocity)

            # mask out bar from bar_stop_pixel until the end
            bar_alpha = np.ones((bar_x, bar_y), dtype=np.uint8) * 255
            bar_alpha[:, bar_stop_pixel:] = 0

            self._logger.debug('bar_alpha shape: {}'.format(bar_alpha.shape))
            gradient_end = int(self._velocity_bar_gradient_end * bar_stop_pixel)
            gradient_space_step = int(gradient_end / self._velocity_bar_gradient_steps)
            gradient_alpha_step = int(255 / self._velocity_bar_gradient_steps)
            for i in range(self._velocity_bar_gradient_steps):
                bar_alpha[:, i*gradient_space_step: (i+1)*gradient_space_step] = i * gradient_alpha_step

            masked_bar = np.dstack((bar, bar_alpha))

            #overlay bar into background
            self._displayed_image = self._overlay(base_image=self._displayed_image, overlay_image=masked_bar, location=location)

    def _map_velocity_to_bar_location(self, velocity):
        """
        this function should translates from velocity to the y pixel that the bar should get to,
        this will define absolute locations for bicycle icons, speed numbers, bar etc
        :param velocity:
        :return: ypixel location of and of bar
        """
        # (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min --> map one spectrum to another
        pixel = velocity * (self._velocity_bar_max_pixel - self._velocity_bar_min_pixel) \
                / (self._velocity_bar_max_velocity - self._velocity_bar_min_velocity) \
                + self._velocity_bar_max_velocity
        return int(pixel)

    def _update_bicycle_logos_placements(self):
        """
        overlay the bicycle logo on the velocity bar in the right location
        :return:
        """
        for player, velocity in self._velocity.items():
            if player == 'player1':
                x_loc = self._player_1_bicycle_icon_x
            else:
                x_loc = self._player_2_bicycle_icon_x

            y_bar_loc = self._map_velocity_to_bar_location(velocity=velocity)
            y_icon_loc = y_bar_loc + self._velocity_bar_bicycle_icon_offset
            self._displayed_image = self._overlay(base_image=self._displayed_image,
                                                  overlay_image=self._images_structures['velocity_bicycle_icon_img'],
                                                  location=(x_loc, y_icon_loc))

    def run(self):
        self._logger.info('starting main loop')
        self._running = True
        cv2.namedWindow('display', cv2.WND_PROP_FULLSCREEN)

        if cv2.__version__ > '2.4.9.1':
            cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

        while self._running:
            if self._target_velocity != self._velocity:
                self._displayed_image = np.copy(self._images_structures['background_img'])
                self._update_current_velocity()

                self._update_power_bar()

                self._update_velocity_bar()

                # show image
                cv2.imshow('display', self._displayed_image)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        self._running = False
        self._logger.info('main loop finished')


if __name__ == '__main__':
    from bicycle_player import init_logging
    init_logging(logger_name='BicycleRaceViewer', logger_level=logging.INFO)
    b = BicycleRaceViewer()
    b.setDaemon(True)
    b.start()
    sleep(2)
    b.update_velocity(player='player1', new_velocity=1)
    sleep(5)
    b.update_velocity(player='player1', new_velocity=30)
    sleep(5)
    b.update_velocity(player='player2', new_velocity=20)
    sleep(5)
    b.update_velocity(player='player1', new_velocity=60)
    while b.is_alive():
        sleep(1)
