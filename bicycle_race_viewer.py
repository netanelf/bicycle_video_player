import threading
import logging
from time import sleep
from os import path
import numpy as np
import cv2


class BicycleRaceViewer(threading.Thread):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initializing {}'.format(self.__class__.__name__))
        super(BicycleRaceViewer, self).__init__()
        self._running = False

        self._velocity = {'player1': 0, 'player2': 0}
        self._target_velocity = {'player1': 0, 'player2': 0}

        # images decelerations
        self.base_image_dir = 'race_viewer_images'
        self.background_img = path.join(self.base_image_dir, 'background.png')
        self.velocity_bicycle_icon_img = path.join(self.base_image_dir, 'png_icon.png')
        self.other_img = path.join(self.base_image_dir, '1')

        # hold all images (icons, background etc.)
        self.images_structures = {}

        # hold the image that will be displayed on screen
        self.displayed_image = None

        self._read_all_images()

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
                self.images_structures[img_name] = cv2.imread(getattr(self, img_name), cv2.IMREAD_UNCHANGED)
                if self.images_structures[img_name] is None:
                    raise Exception('could not find img: {}'.format(img_name))

            except Exception as ex:
                self._logger.error('could not read img: {}, ex: {}'.format(img_name, ex))

        # ensure background image is fully opaque (rgb with no apha channel)
        background = self.images_structures['background_img']
        (x_dim, y_dim, z_dim) = background.shape
        self._logger.debug('background_img dimensions: {}'.format((x_dim, y_dim, z_dim)))
        if z_dim == 4:
            self._logger.error('background_img has only 3 channels, adding alpha')
            self.images_structures['background_img'] = background[:, :, 0:3]
            self._logger.info('new dimension: {}'.format(self.images_structures['background_img'].shape))

        self._logger.info('finished reading all images into cv objects')

    def update_velocity(self, player, new_velocity):
        #update target velocity
        pass

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
        for player, velocity in self._velocity.items():
            if velocity > 3:
                pass
            elif velocity > 2:
                pass
            elif velocity > 1:
                pass
            else:
                self.displayed_image = self._overlay(base_image=self.displayed_image, overlay_image=self.images_structures['velocity_bicycle_icon_img'], location=(20, 50))

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
        pass
        # bar width + gradient
        # bicycle logo placement
        # km"sh location update
        # digits update + location

    def _update_current_velocity(self):
        # update self._velocity to next step
        pass

    def run(self):
        self._logger.info('starting main loop')
        self._running = True
        cv2.namedWindow('display', cv2.WND_PROP_FULLSCREEN)

        if cv2.__version__ > '2.4.9.1':
            cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        else:
            cv2.setWindowProperty('display', cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

        while self._running:
            self.displayed_image = self.images_structures['background_img']
            self._update_current_velocity()

            self._update_power_bar()

            self._update_velocity_bar()


            # show image
            cv2.imshow('display', self.displayed_image)
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

    while b.is_alive():
        sleep(1)
