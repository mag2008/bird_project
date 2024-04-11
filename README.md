This code streams audio and video and record if motion is detected in the video and sends the file to the FTP server

install libreries with:
sudo apt install python3-pyaudio
pip install opencv-python

make a FTP directory in both raspberry pi as well as on the FTP server with video audio both as subdirectory
copy the v4l2_bash.sh in to Documents if video has to be enbrightened

set the default microphone:
https://github.com/microsoft/IoT-For-Beginners/blob/main/6-consumer/lessons/1-speech-recognition/pi-microphone.md

run the code "host_server14.py" on your raspberry pi

activate the video and audio in obs studio nd motion detection will start

