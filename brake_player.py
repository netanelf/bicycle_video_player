from main_controller import VlcPlayer


class BrakePlayer(VlcPlayer):
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
