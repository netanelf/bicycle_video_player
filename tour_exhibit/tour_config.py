import collections
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
                                        
SCENES = collections.OrderedDict([
    ('default', collections.OrderedDict([
                                        ('front_movie', 'jerusalem_front.mp4'),
                                        ('back_movie', 'jerusalem_back.mp4'),
                                        ('topography', collections.OrderedDict([
                                                                                (0, 1),
                                                                                (5000, 0),   
                                                                                (10000, 1),
                                                                                (20000, 0),
                                                                                (30000, 2),
                                                                                (40000, 0),
                                                                                (50000, 0),
                                                                                (60000, 1),
                                                                                (70000, 0),
                                                                                (80000, 1),
                                                                                (90000, 2)
                                                                               ]))
                                       ])
     ),
    ('breman', collections.OrderedDict([
                                        ('front_movie', 'breman_front.mp4'),
                                        ('back_movie', 'breman_back.mp4'),
                                        ('topography', collections.OrderedDict([
                                                                                (0, 1),
                                                                                (5000, 0),   
                                                                                (10000, 1),
                                                                                (20000, 0),
                                                                                (30000, 2),
                                                                                (40000, 0),
                                                                                (50000, 0),
                                                                                (60000, 1),
                                                                                (70000, 0),
                                                                                (80000, 1),
                                                                                (90000, 2)
                                                                               ]))
                                       ])
     ),
    ('ottawa', collections.OrderedDict([
                                        ('front_movie', 'ottawa_front.mp4'),
                                        ('back_movie', 'ottawa_front.mp4'),
                                        ('topography', collections.OrderedDict([
                                                                                (0, 1),
                                                                                (5000, 0),   
                                                                                (10000, 1),
                                                                                (20000, 0),
                                                                                (30000, 2),
                                                                                (40000, 0),
                                                                                (50000, 0),
                                                                                (60000, 1),
                                                                                (70000, 0),
                                                                                (80000, 1),
                                                                                (90000, 2)
                                                                               ]))
                                       ])
     ),
    ('napoli', collections.OrderedDict([
                                        ('front_movie', 'napoli_front.mp4'),
                                        ('back_movie', 'napoli_back.mp4'),
                                        ('topography', collections.OrderedDict([
                                                                                (0, 1),
                                                                                (5000, 0),   
                                                                                (10000, 1),
                                                                                (20000, 0),
                                                                                (30000, 2),
                                                                                (40000, 0),
                                                                                (50000, 0),
                                                                                (60000, 1),
                                                                                (70000, 0),
                                                                                (80000, 1),
                                                                                (90000, 2)
                                                                               ]))
                                       ])
     ),
    ('ottawa_night', collections.OrderedDict([
                                        ('front_movie', 'ottawa_night_front.mp4'),
                                        ('back_movie', 'ottawa_night_front.mp4'),
                                        ('topography', collections.OrderedDict([
                                                                                (0, 1),
                                                                                (5000, 0),   
                                                                                (10000, 1),
                                                                                (20000, 0),
                                                                                (30000, 2),
                                                                                (40000, 0),
                                                                                (50000, 0),
                                                                                (60000, 1),
                                                                                (70000, 0),
                                                                                (80000, 1),
                                                                                (90000, 2)
                                                                               ]))
                                       ])
     )
])


# speed = encoder_delta(in one second) / ENCODER_TO_SPEED_CONVERSION  
ENCODER_TO_SPEED_CONVERSION = 10

# if speed is greater than SPEED_THRESHOLD, movie will be played
SPEED_THRESHOLD = 10

DEBOUNCING_TIME = 0.5  #[S]

TIME_FOR_RETURN_TO_DEFAULT_SCENE = 30  # [S]

# [('dwell time', 'speed'), (0.4[S], 0.9xNormal)]
"""
SPEED_UP_RAMPING = [
    (0.5, 0.3),
    (0.5, 0.4),
    (0.5, 0.5),
    (0.5, 0.6),
    (0.5, 0.7),
    (0.5, 0.8),
    (0.5, 0.9),
] """
SPEED_UP_RAMPING = [
    (0, 0.3)
]

# [('dwell time', 'speed'), (0.4[S], 0.9xNormal)]
"""
SPEED_DOWN_RAMPING = [
    (0.5, 0.9),
    (0.5, 0.8),
    (0.5, 0.7),
    (0.5, 0.6),
    (0.5, 0.5),
    (0.5, 0.4),
    (0.5, 0.3),
]"""
SPEED_DOWN_RAMPING = [
    (0, 0.9)
]
