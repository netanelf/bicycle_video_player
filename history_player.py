from main_controller import VlcPlayer


class HistoryPlayer(VlcPlayer):
    CFG = 0 #todo
    MOVIE = "" #todo

    def __init__(self,serial):
        super(self, self.init())
        self.thresh = self.CFG
        self.load_movie(self.MOVIE)

    def run(self):
        while True:
            pass
            # use self.speed
