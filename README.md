# H264_Conver
converting mjpeg to h264


Switch to python3.8  (because the code is written for python 3.8)
https://tech.serhatteker.com/post/2019-12/upgrade-python38-on-ubuntu/

```
python3 demo.py 2>/dev/null  
```
This `demo.py` pipeline will create raw frames and then encoder thread will encode it. after encoding the decoder thread will read the encoded chunck and decode it.



---
Thanks to https://stackoverflow.com/questions/60462840/ffmpeg-delay-in-decoding-h264

