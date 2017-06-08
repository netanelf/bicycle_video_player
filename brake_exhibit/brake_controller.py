from json import encoder

from main_controller import VlcPlayer
import time
import brake_config as cfg

class BrakeController(VlcPlayer):

    def __init__(self):
        super(BrakeController, self).__init__()
        self._encoder_data = 0
        self._prev_video_speed = 0
        self.load_movie(cfg.MOVIE)

    def run(self):
        threshold_passed = False
        while self._alive:
            for key in sorted(cfg.THRESHOLD.keys(), reverse=True):
                if self._encoder_data >= cfg.THRESHOLD[key]:
                    if self._prev_video_speed != cfg.VID_SPEED[key]:
                        self.update_speed(cfg.VID_SPEED[key])
                        self._prev_video_speed = cfg.VID_SPEED[key]
                    if not self._is_playing:
                        self.play()
                    threshold_passed = True
                    break
            if not threshold_passed:
                if self._is_playing:
                    self.pause()
            threshold_passed = False
            time.sleep(0.05)

    def update_encoder(self, player_id, encoder_data):
        self._encoder_data = encoder_data

if __name__ =='__main__':
    b = BrakeController()
    while b.player.is_alive():
        time.sleep(1)