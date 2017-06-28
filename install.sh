sudo apt-get update -y
sudo apt-get install python-serial -y
sudo apt-get install vlc -y
sudo apt-get install git -y
sudo apt-get install python-pip -y
sudo apt-get install python-numpy -y
sudo apt-get install python-opencv -y
sudo apt-get install python-serial -y
sudo apt-get install vlc -y
sudo usermod -a -G dialout $USER
cd ~/
git clone https://github.com/netanelf/bicycle_video_player
cd ~/bicycle_video_player
chmod +x achbar.sh
mkdir ~/.config
mkdir ~/.config/autostart
cp run_race_player.desktop ~/.config/autostart
echo "Installation completed. Restarting in 1 minute"
shutdown -r -t 1
