#!/bin/bash

nohup /home/mada/bicycle_video_player/achbar.sh &
cd /home/mada/bicycle_video_player
python ./main_controller.py
