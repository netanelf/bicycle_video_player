import logging
import os

# this is just for debug running through the __main__ function
try:
    from main_controller import VlcPlayer
except ImportError:
    import sys
    sys.path.append('..')
    from main_controller import VlcPlayer
import tour_config as cfg
import time


class TourController(VlcPlayer):

    topographies = {'DOWN_HILL': 0,
                    'UP_HILL': 1,
                    'MISHOR': 2
                    }

    def __init__(self, player_number):
        super(TourController, self).__init__(num_of_mps=len(cfg.SCENES))
        self._logger = logging.getLogger(self.__class__.__name__)
        self._loading_file = False
        self._speed = 0
        self._player_number = player_number

        self._topography_struct = None
        self._topography_keys = None
        self._current_topography_index = None
        self._last_movie_change_time = time.time() - 5
        self._movie_stopped_time = time.time()
        self._played_since_movie_reset = False
        if self._player_number == 0:
            self._movie_type = 'front_movie'
        else:
            self._movie_type = 'back_movie'
        self._load_all_scenes()
        self._active_player_id = 0
        self._set_active_scene(scene_name='default')
        self._logger.info('finished initializing TourController')

    def _load_all_scenes(self):
        self._logger.info('in _load_all_scenes')
        media_id = 0
        for scene_name, scene in cfg.SCENES.items():
            file_name = cfg.SCENES[scene_name][self._movie_type]
            file_path = os.path.join(os.path.basename(os.path.dirname(os.path.realpath(__file__))), file_name)
            self._logger.info('loading scene: {}, file: {}, media_id: {}'.format(scene_name, file_name, media_id))
            self.load_movie(file=file_path, media_sel=media_id)
            self.set_fullscreen(media_sel=media_id)
            media_id += 1

    def _set_active_scene(self, scene_name):
        self._logger.info('setting active scene to: {}'.format(scene_name))
        self._topography_struct = cfg.SCENES[scene_name]['topography']
        self._topography_keys = self._topography_struct.keys()
        self._current_topography_index = -1
        self._start_paused_movie()

    def run(self):
        while self._alive:
            if not self._loading_file:
                if self._speed > cfg.SPEED_THRESHOLD and self.is_playing(self._active_player_id) is False:
                    self._start_gradual_playing()

                if self._speed <= cfg.SPEED_THRESHOLD and self.is_playing(self._active_player_id) is True:
                    self._start_gradual_stopping()
                
                if self.is_playing(self._active_player_id) is False and time.time() - self._movie_stopped_time > cfg.TIME_FOR_RETURN_TO_DEFAULT_SCENE and (self._active_player_id != 0 or self.get_time(self._active_player_id) > 100) and self._played_since_movie_reset:
                    self._logger.debug('bicycle idle for {} time, returning to default scene'.format(time.time() - self._movie_stopped_time))
                    
                    if self._active_player_id == 0:
                        self.set_position(0)
		        self._current_topography_index = -1

                    else:
                        self._active_player_id = 0
                        self._set_active_scene(scene_name=cfg.SCENES.keys()[self._active_player_id])
                        self._last_movie_change_time = time.time()
                        self._movie_stopped_time = time.time()
                        
                    self._played_since_movie_reset = False
                    self.play(self._active_player_id)
                    time.sleep(1)
                    self.pause(self._active_player_id)
                    self._logger.debug('returning to main loop')

                t = self.get_time(self._active_player_id)
                self._logger.debug('time: {}'.format(t))

                if self._current_topography_index + 1 < len(self._topography_keys) and self.is_playing(self._active_player_id) is True:
                    self._logger.debug('next topography time: {}'.format(self._topography_keys[self._current_topography_index + 1]))
                    if t >= self._topography_keys[self._current_topography_index + 1]:  # we just passed to next topography
                        self._current_topography_index += 1
                        self._set_topography(self._topography_struct[self._topography_keys[self._current_topography_index]])
            file_path = os.path.join(os.path.basename(os.path.dirname(os.path.realpath(__file__))), cfg.SCENES[cfg.SCENES.keys()[self._active_player_id]][self._movie_type])
            if (self.restart_ended_video(file_path, self._active_player_id)):
		self._current_topography_index = -1
            time.sleep(0.05)

    def _start_paused_movie(self):
        self.play(self._active_player_id)
        time.sleep(1)
        self.pause(self._active_player_id)

        for i in range(len(cfg.SCENES)):
            if i != self._active_player_id:
                self.stop(media_sel=i)

    def _set_topography(self, topography):
        """
        fan_0
        fan_1
        load_0
        load_1
        :param topography:
        :return:
        """
        self._logger.debug('in _set_topography, topography: {}'.format(topography))
        if topography == self.topographies['DOWN_HILL']:
            self.data_to_send.put('load_0')
            self.data_to_send.put('fan_1')
        elif topography == self.topographies['UP_HILL']:
            self.data_to_send.put('fan_0')
            self.data_to_send.put('load_1')
        elif topography == self.topographies['MISHOR']:
            self.data_to_send.put('load_0')
            self.data_to_send.put('fan_0')
        else:
            self._logger.error('unknown topography ({})'.format(topography))

    def _start_gradual_playing(self):
            self._logger.debug('in _start_gradual_playing ')
            self._played_since_movie_reset = True
            self.play(media_sel=self._active_player_id)
            self.gradual_speed_change(steps=cfg.SPEED_UP_RAMPING, media_sel=self._active_player_id)

            # if we start.
            if self._topography_keys[self._current_topography_index] != self.topographies['MISHOR'] and \
                            self._current_topography_index != -1:
                self._logger.debug('going back to topography: {}'.format(self._topography_struct[self._topography_keys[self._current_topography_index]]))
                self._set_topography(topography=self._topography_struct[self._topography_keys[self._current_topography_index]])

            self.update_speed(new_speed=1, media_sel=self._active_player_id)
        
    def _start_gradual_stopping(self):
        self._logger.debug('in _start_gradual_stopping ')
        self.gradual_speed_change(steps=cfg.SPEED_DOWN_RAMPING, media_sel=self._active_player_id)
        self.pause(media_sel=self._active_player_id)

        # if we stop we should stop the FAN etc.
        if self._topography_struct[self._topography_keys[self._current_topography_index]] != self.topographies['MISHOR']:
            self._logger.debug('setting to MISHOR (due to stopping of movement)')
            self._set_topography(topography=self.topographies['MISHOR'])

        self._movie_stopped_time = time.time()

    def do_kaftor(self, kaftor_number):
        self._logger.info('button {} was pushed'.format(kaftor_number))
        if (kaftor_number == 1) and (self.is_playing(self._active_player_id) is False) and (time.time() - self._last_movie_change_time > cfg.DEBOUNCING_TIME):
            self._loading_file = True
            if self._active_player_id + 1 < len(cfg.SCENES.keys()):
                self._active_player_id += 1
            else:
                self._active_player_id = 0

            self._set_active_scene(scene_name=cfg.SCENES.keys()[self._active_player_id])
            self._last_movie_change_time = time.time()
            self._loading_file = False
            self._played_since_movie_reset = True
            self._movie_stopped_time = time.time()

    def update_encoder(self, player_id, encoder_data):
        self._logger.debug('in update_encoder, player_id= {}, encoder_data= {}'.format(player_id, encoder_data))
        self._speed = encoder_data / float(cfg.ENCODER_TO_SPEED_CONVERSION)
        
        
def init_logging(log_name, logger_level):
    logger = logging.getLogger()
    s_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(filename=os.path.join('..', 'logs', '{}_{}.log'.format(
        log_name,
        datetime.now().strftime('%d-%m-%y_%H-%M-%S'))),
                                    maxBytes=10E6,
                                    backupCount=500)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    logger.setLevel(logger_level)
    
if __name__ == '__main__':
    from logging.handlers import RotatingFileHandler
    from datetime import datetime
    init_logging('tour_controller', logging.INFO)
    p = TourController(player_number=0)
    p.setDaemon(True)
    p.start()
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=3000)
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=1001)
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=500)
    time.sleep(10)

    p.do_kaftor(kaftor_number=0)

    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=3000)
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=1001)
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=500)
    time.sleep(10)

    p.do_kaftor(kaftor_number=0)

    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=3000)
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=1001)
    time.sleep(5)
    p.update_encoder(player_id=0, encoder_data=500)
    time.sleep(10)
