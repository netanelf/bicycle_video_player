
GRAPHICS_DICTIONARY = 'race_exhibit/bicycle_race_sample_pics'

# Velocity Bar
VELOCITY_BAR_LOCATION = ((154, 438), (350, 438))  # upper left pixel ((player_1_x, player_1_y), (player_2_x, player_2_y))
VELOCITY_BAR_SIZE = (115, 980, 3)  # in pixels (x_dim, y_dim, z_dim)
VELOCITY_BAR_1_COLOR = (50, 255, 0)  # RGB
VELOCITY_BAR_2_COLOR = (0, 205, 255)  # RGB
BICYCLE_ICON_VERTICAL_OFFSET = 5   # offset of bicycle icon from bar end
BICYCLE_ICON_HORIZONTAL_OFFSET = -140    # offset of bicycle icon from bar end


# Power Bar
POWER_BAR_LOCATION = ((650, 100), (650, 800))

SPEED_FACTOR = [6, 6, 3]

SPEED_STATE_THRESHOLDS = range(0, 80, 3)  # speed threshold for power bars

# Currently not used (digits in power bar)
POWER_DIGITS_SCALING = 1
POWER_BAR_DIGIT_OFFSET = [300, 300]
SPEED_POWER_CONVERSION_FACTOR = 2  # power = speed * factor

VELOCITY_DIGITS_SCALING = 1
VELOCITY_BAR_SPEED_OFFSET = [60, 60]
PLAYER_1 = 0
PLAYER_2 = 1
PLAYER_1_COLOR = 'green'
PLAYER_2_COLOR = 'yellow'

DAILY_RECORD_COLOR = 'white'
RECORD_DIGIT_LOCATION = [240, 213]
