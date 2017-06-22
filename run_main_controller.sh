#!/bin/bash
gsettings set org.gnome.desktop.screensaver idle-activation-enabled false
gsettings set org.gnome.settings-daemon.plugins.power active false
cd /home/mada/bicycle_video_player
python main_controller.py 
