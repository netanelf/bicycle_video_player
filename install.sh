#!/bin/bash

if (( EUID == 0 )); then
	echo 'Please run without sudo!' 1>&2
	exit 1
fi

cd "$(dirname "${BASH_SOURCE[0]}")"

sudo apt update
sudo apt install -y git python2 vlc htop

wget -qO- https://bootstrap.pypa.io/get-pip.py | sudo python2

pip2 install numpy pyserial opencv-python==3.4.8.29 # ==3.4.0.14

cd ~
git clone https://github.com/netanelf/bicycle_video_player.git
cd ~/bicycle_video_player
chmod +x achbar.sh
mkdir -p ~/.config/autostart/
cp run_race_player.desktop ~/.config/autostart/

sudo usermod -a -G dialout $USER

echo "Installation completed. Restarting in 1 minute"
shutdown -r -t 1
