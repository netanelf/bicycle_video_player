
'''

'DOWN_HILL': 0,
'UP_HILL': 1,
'MISHOR': 2

SCENES = {
    'scene_name': {
        'front_movie': r'path_to_front_movie',
        'back_movie': r'path_to_back_movie',
        'topography': [(frame_number, 0), (frame_number2, 2), (frame_start, topography)]
    },
}
'''
SCENES = {
    'default': {
        'front_movie': r'movie.mp4',
        'back_movie': r'movie.mp4',
        'topography': [(0, 2), (100, 0)]
    },
}


# speed = encoder_delta(in one second) / ENCODER_TO_SPEED_CONVERSION  
ENCODER_TO_SPEED_CONVERSION = 100

# if speed is greator than SPEED_THRESHOLD, movie will be played
SPEED_THRESHOLD = 10


# [('dwell time', 'speed'), (0.4[S], 0.9xNormal)]
SPEED_UP_RAMPING = [
    (0.5, 0.3),
    (0.5, 0.6),
    (0.5, 0.9),
]