from json import encoder

from main_controller import VlcPlayer
import time
import brake_config as cfg

class BrakeController(VlcPlayer):

    def __init__(self):
        super(BrakeController, self).__init__(num_of_mps=1)
        self._encoder_data = 0
        self._prev_video_speed = 0
        self._cur_movie = 0
        self.load_movie(cfg.MOVIE1,0)
        self.set_fullscreen(0)

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

if __name__ =='__main__':
    b = Try()
    b.set_fullscreen(media_sel=0)
    b.set_fullscreen(media_sel=1)
    not_switched = True
    b.play(b._cur_movie)
    while (not_switched):
        time.sleep(0.05)
        if b.get_time(b._cur_movie) > 18000:
            print "switching movie"
            b.switch_movie(0,1)
            not_switched = False
    time.sleep(20)

    """

