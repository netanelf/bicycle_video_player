# bicycle_video_player
1. install python (2.7.13 https://www.python.org/)
2. install numpy (pip install numpy)
3. install git (2.13.0)
4. git clone https://github.com/netanelf/bicycle_video_player.git
5. install opencv (3.2.0-vc14)
6. copy cv2.pyd to: C:\Python27\Lib\site-packages


# Linux
1. install git (sudo apt-get install git)
2. git clone https://github.com/netanelf/bicycle_video_player.git
3. install numpy (sudo apt-get install python-numpy)
4. install pyserial (sudo apt-get install python-serial)
5. install opencv (sudo apt-get install python-opencv)
6. add user permissions to dialout group: 'sudo usermod -a -G dialout <username>' and then logout and login


# exhibits
Arduino ID legend - MSB -> ▯▯▯▯ <- LSB

for each ▯, 1 = add jumper, 0 = leave without jumper

## History:
screen: 1

bicycle: 3

arduino_0: 1111

arduino_1: 1110

arduino_2: 1101

## City Tour:
screen: 2

bicycle: 2

arduino_0: 1100

arduino_1: 1011

arduino_2: 1010

arduino_3: 1001

## Brakes:
screen:1

arduino_0: 1000


## Race:

### Donkey (two big bicycles)
screen: 1

bicycle: 2

arduino_0: 0111

arduino_1: 0110

### Donkey-Foal (hand + small bicycle)
screen: 1

bicycle: 2

arduino_2: 0101

arduino_3: 0100




