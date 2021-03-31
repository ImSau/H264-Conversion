"""
[RGB frame] ------ encoder ------> [h264 stream] ------ decoder ------> [RGB frame]
              ^               ^                    ^               ^
        encoder_write    encoder_read        decoder_write    decoder_read
"""



import subprocess
from queue import Queue
from threading import Thread
from time import sleep, time
import numpy as np
import cv2
import sys

WIDTH = 224
HEIGHT = 224
NUM_FRAMES = 1

#global chunk

def t(epoch=time()):
    return int(time() - epoch)

def compare_frames(frame, x):
    """
    unused for now, It was to compare i/p & o/p numpy.ndarray
    """
    comparison = (frame == x) 
    equal_arrays = comparison.all() 
    print(equal_arrays)


def make_frames(num_frames):
    print('****Making Frames*****')
    x = np.arange(WIDTH, dtype=np.uint8)
    # print("x:", x)
    # print("x_shape:", x.shape)
    # print("-----------")
    x = np.broadcast_to(x, (num_frames, HEIGHT, WIDTH))
    # print("x2:", x)
    # print("x2_shape:", x.shape)
    # print("-----------")
    x = x[..., np.newaxis].repeat(3, axis=-1)
    # print("x3_shape:", x.shape)
    # print("x3:", x)
    # print("-----------")
    x[..., 1] = x[:, :, ::-1, 1]
    # print("x4_shape:", x.shape)
    # print("x4:", x[..., 1])
    scale = np.arange(1, len(x) + 1, dtype=np.uint8)
    # print("scale:" , scale)
    scale = scale[:, np.newaxis, np.newaxis, np.newaxis]
    # print("scale:" , scale)
    x *= scale
    #print(x)
    # _, jpg_frame = cv2.imencode('test.jpg', x)
    # #cv2.imwrite('text.jpg', x)
    # #cv2.waitKey()
    return x

def encoder_write(writer):
    """Feeds encoder frames to encode"""
    frames = make_frames(num_frames=NUM_FRAMES)
    
    print("-----------")
    print("len:", len(frames))
    print("type:", type(frames))
    #print(frames)
    for i, frame in enumerate(frames):
        #print(frames[i])
        cv2.imwrite('input%i.jpg'%i, frames[i])

        print("i:", i)
        writer.write(frame.tobytes())
        print("Sizeof_Frame_To_Byte:", sys.getsizeof(frame.tobytes()))
        # writer.write(frame.tobytes())
        #print("Frame_To_Bytes:\n", frame.tobytes())
        """{i + 1:<3}
        i+=1
        if(i<3):
            frames=i
        """
        writer.flush()
        print(f"time={t()} frames={i + 1:<3} encoder_write")
        print("Ek aur baar i:", i)
        print("Sone Jaa Raha Hoon")
        sleep(2)
        print("Jaag Gya")
    writer.close()

def encoder_read(reader, queue):
    """Puts chunks of encoded bytes into queue"""
    # print("chunk")
    # print()

    while chunk:= reader.read1():
        print(type(chunk))
        print("chunk:", chunk)
        print("chunkSize:", sys.getsizeof(chunk))
        #putting in queue
        queue.put(chunk)

        #print("QueueSize:", queue.qsize())
        print("----")
        print("QueueSize:", sys.getsizeof(queue))
        #print(queue.get())
        print(f"time={t()} chunk={len(chunk):<4} encoder_read")
    queue.put(None)


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
    targets = make_frames(num_frames=NUM_FRAMES)
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
            cv2.imwrite('output%i.jpg'%i, frame)
            psnr = 10 * np.log10(255**2 / np.mean((frame - targets[i])**2))
            buffer = buffer[frame_len:]
            #print(buffer)
            i += 1
            print(f"time={t()} frames={i:<3} decoder_read  psnr={psnr:.1f}")

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


cmd = (
    "ffmpeg "
    "-f rawvideo -pix_fmt rgb24 -s 224x224 "
    "-i pipe: "
    "-vcodec libx264 "
    "-f flv "
    "-tune zerolatency "
    "pipe:"
)
encoder_process = subprocess.Popen(
    cmd.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE
)

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

queue = Queue()

threads = [
    Thread(target=encoder_write, args=(encoder_process.stdin,),),
    Thread(target=encoder_read, args=(encoder_process.stdout, queue),),
    Thread(target=decoder_write, args=(decoder_process.stdin, queue),),
    Thread(target=decoder_read, args=(decoder_process.stdout,),),
]

for thread in threads:
    thread.start()