from main_controller import VlcPlayer
import config as cfg

class BrakeController(VlcPlayer):
    CFG = 0 #todo
    MOVIE = "" #todo

    def __init__(self,serial):
        super(self, self.init())
        self.thresh = self.CFG
        self.load_movie(self.MOVIE)

    def do_kaftor(kaftor_number):
        pass

    def run(self):
        while True:
            pass
            # use self.speed

    def has_send(self):
        pass
        # read time/ frame

    def do_kaftor(self,kaftor_number):
        #TODO
        pass

    def update_encoder(self, player_id, encoder_data):
        #TODO
        pass

if __name__ =='__main__':
    init_logging(log_name='main_controller', logger_level=logging.INFO)
    b = BrakeController()
    while b.player.is_alive():
        time.sleep(1)