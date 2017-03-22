import threading
import logging
from time import sleep
import cv2


class BicycleRaceViewer(threading.Thread):
    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info('initializing {}'.format(self.__class__.__name__))
        super(BicycleRaceViewer, self).__init__()
        self._velocity = {'player1': 0, 'player2': 0}
        self._target_velocity = {'player1': 0, 'player2': 0}


    def update_velocity(self, player, new_velocity):
        #update target velocity
        pass

    def _update_power_bar(self):
        # accprding tp self.velocity:
        # update images for both players
        self.update_power_bar_digits()

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
        while self.running:
            self._update_current_velocity()

            self._update_power_bar()
            self._update_power_bar_digits()
            self._update_velocity_bar()


            # show image


if __name__ == '__main__':
    b = BicycleRaceViewer()
    b.setDaemon(True)
    b.start()
    sleep(20)
