import time

from main_controller import VlcPlayer
import config


class HistoryController(VlcPlayer):
    MOVIE = "movie.mp4"

    def __init__(self):
        super(HistoryController, self).__init__()
        self.thresh = config.THRESHOLD
        self.load_movie(self.MOVIE)
        self.d={}

    def run(self):
        while True:
            time.sleep(0.1)
            toggle = 0
            for key, value in self.d.iteritems():
                if value > self.thresh:
                    toggle = 1
                    break
            if toggle == 1 :
                self.play()
            else:
                self.pause()



    def update_encoder(self, player_id, encoder_data):
        self.d[player_id] = encoder_data*config.CONVERSION_FACTOR
