
"""

'DOWN_HILL': 0,
'UP_HILL': 1,
'MISHOR': 2

SCENES = {
    'scene_name': {
        'front_movie': r'path_to_front_movie',
        'back_movie': r'path_to_back_movie',
        'topography': {time_ms: 0,
                       time_ms2: 2,
                       time_ms3, 1)}
    },
}

ENSURE that the timestamps are in order ie. time_ms3 >= time_ms2 >= time_ms
"""
SCENES = {
    'default': {
        'front_movie': r'tour_exhibit\movie.mp4',
        'back_movie': r'movie.mp4',
        'topography': {0: 1,
                       5000: 2,
                       12000: 0
                       }
    },
}


# speed = encoder_delta(in one second) / ENCODER_TO_SPEED_CONVERSION  
ENCODER_TO_SPEED_CONVERSION = 100

# if speed is greater than SPEED_THRESHOLD, movie will be played
SPEED_THRESHOLD = 1

# [('dwell time', 'speed'), (0.4[S], 0.9xNormal)]
SPEED_UP_RAMPING = [
    (0.5, 0.3),
    (0.5, 0.4),
    (0.5, 0.5),
    (0.5, 0.6),
    (0.5, 0.7),
    (0.5, 0.8),
    (0.5, 0.9),
]

# [('dwell time', 'speed'), (0.4[S], 0.9xNormal)]
SPEED_DOWN_RAMPING = [
    (0.5, 0.9),
    (0.5, 0.8),
    (0.5, 0.7),
    (0.5, 0.6),
    (0.5, 0.5),
    (0.5, 0.4),
    (0.5, 0.3),
]