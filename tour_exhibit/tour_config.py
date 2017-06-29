
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
        'front_movie': 'ottawa_bicycle_daytime.mp4',
        'back_movie': 'ottawa_bicycle_daytime.mp4',
        'topography': {0: 1,
                       5000: 2,
                       12000: 0
                       }
    },
    'vienna': {
        'front_movie': 'ottawa_night_time_1.mp4',
        'back_movie': 'ottawa_night_time_1.mp4',
        'topography': {0: 1,
                       5000: 2,
                       12000: 0
                       }
    },
}


# speed = encoder_delta(in one second) / ENCODER_TO_SPEED_CONVERSION  
ENCODER_TO_SPEED_CONVERSION = 10

# if speed is greater than SPEED_THRESHOLD, movie will be played
SPEED_THRESHOLD = 10

DEBOUNCING_TIME = 0.5  #[S]

TIME_FOR_RETURN_TO_DEFAULT_SCENE = 30  # [S]

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
