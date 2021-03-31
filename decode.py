import subprocess
from queue import Queue
from threading import Thread
from time import sleep, time
import numpy as np
import cv2
import sys
import re

WIDTH = 224
HEIGHT = 224
NUM_FRAMES = 1

def t(epoch=time()):
    return int(time() - epoch)

f = open("queue_file1", "rb")
#print(f.read()
x=f.read()
print(type(x))
print(x)
#print(re.sub(b"HELLLLLLLOOOOOOOOOOOOO", '', x)

queue = Queue()


queue.put(x)

def decoder_write(writer, queue):
    """Feeds decoder bytes to decode"""
    #Getting in Queue


    while chunk:= queue.get():
        #Yaha decode ho chuka hai
        writer.write(chunk)
        #print("Decoded_Chunk:", chunk)

        writer.flush()
        print(f"time={t()} chunk={len(chunk):<4} decoder_write")
    writer.close()

def decoder_read(reader):
    """Retrieves decoded frames"""
    buffer = b""
    frame_len = HEIGHT * WIDTH * 3
    #targets = make_frames(num_frames=NUM_FRAMES)
    i = 0
    while chunk:= reader.read1():
        buffer += chunk
        #print("Buffer:", buffer)
        #print("It was buffer")
        while len(buffer) >= frame_len:
            frame = np.frombuffer(buffer[:frame_len], dtype=np.uint8)
            frame = frame.reshape(HEIGHT, WIDTH, 3)
            #print(frame)
            # print("cf:", y=compare_frames(frame, x))
            print("frame_shape:", frame.shape)
            cv2.imwrite('D_output%i.jpg'%i, frame)
           #psnr = 10 * np.log10(255**2 / np.mean((frame - targets[i])**2))
            buffer = buffer[frame_len:]
            #print(buffer)
            i += 1
            print(f"time={t()} frames={i:<3} decoder_read ")


# cmd = (
#     "ffmpeg "
#     "-f rawvideo -pix_fmt rgb24 -s 224x224 "
#     "-i pipe: "
#     "-f h264 "
#     "-tune zerolatency "
#     "pipe:"
# )
# encoder_process = subprocess.Popen(
#     cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE
# )

# cmd = (
#     "ffmpeg "
#     "-probesize 32 "
#     "-flags low_delay "
#     "-f h264 "
#     "-i pipe: "
#     "-f rawvideo -pix_fmt rgb24 -s 224x224 "
#     "pipe:"
# )
# decoder_process = subprocess.Popen(
#     cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE
# )


# cmd = (
#     "ffmpeg "
#     "-f rawvideo -pix_fmt rgb24 -s 224x224 "
#     "-i pipe: "
#     "-vcodec libx264 "
#     "-f flv "
#     "-tune zerolatency "
#     "pipe:"
# )
# encoder_process = subprocess.Popen(
#     cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE
# )

cmd = (
    "ffmpeg "
    "-probesize 32 "
    "-flags low_delay "
    "-f flv "
    "-vcodec h264 "
    "-i pipe: "
    "-f rawvideo -pix_fmt rgb24 -s 224x224 "
    "pipe:"
)

decoder_process = subprocess.Popen(
    cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE
)


threads = [
    Thread(target=decoder_write, args=(decoder_process.stdin, queue),),
    Thread(target=decoder_read, args=(decoder_process.stdout,),),
]

for thread in threads:
    thread.start()