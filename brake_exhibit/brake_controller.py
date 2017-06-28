from json import encoder

from main_controller import VlcPlayer
import time
import brake_config as cfg
import generated_vlc as vlc


class BrakeController(VlcPlayer):

    def __init__(self):
        super(BrakeController, self).__init__(num_of_mps=1)
        self._encoder_data = 0
        self._prev_video_speed = 0
        self._cur_movie = 0
        self.load_movie(cfg.MOVIE1)
        self.set_fullscreen()

    def run(self):
        threshold_passed = False
        while self._alive:
            for key in sorted(cfg.THRESHOLD.keys(), reverse=True):
                if self._encoder_data >= cfg.THRESHOLD[key]:
                    if self._prev_video_speed != cfg.VID_SPEED[key]:
                        self.update_speed(cfg.VID_SPEED[key])
                        self._prev_video_speed = cfg.VID_SPEED[key]
                    if not self.is_playing(self._cur_movie):
                        self.play(self._cur_movie)
                    threshold_passed = True
                    break
            if not threshold_passed:
                if self.is_playing(self._cur_movie):
                    self.pause(self._cur_movie)

            #this is a workaround to restart the video when it finishes
            self.restart_ended_video(cfg.MOVIE1,0)

            threshold_passed = False
            time.sleep(0.05)

    def update_encoder(self, player_id, encoder_data):
        self._encoder_data = encoder_data

    def switch_movie(self, old_movie, new_movie):
        self.pause(old_movie)
        self.play(new_movie)
        self._cur_movie = new_movie

"""
class Try(VlcPlayer):

    def __init__(self):
        super(Try, self).__init__(num_of_mps=2)
        self._cur_movie = 0
        self.load_movie(cfg.MOVIE4,0)
        self.load_movie(cfg.MOVIE5,1)

    def switch_movie(self, old_movie, new_movie):
        self.pause(old_movie)
        self.play(new_movie)
        self._cur_movie = new_movie
"""
if __name__ =='__main__':
    b = BrakeController()
    b.start()
    countr = 10
    while (True):
        time.sleep(1)
        countr = countr -1
        b.update_encoder(0,countr)
        if countr == 5:
            countr = 10


