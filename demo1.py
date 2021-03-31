import cv2
import numpy as np
import subprocess as sp
import json

width, height, n_frames, fps = 256, 256, 100, 1  # 100 frames, resolution 256x256, and 1 fps


def make_raw_frame_as_bytes(i):
    """ Build synthetic "raw BGR" image for testing, convert the image to bytes sequence """
    p = width//60
    img = np.full((height, width, 3), 60, np.uint8)
    cv2.putText(img, str(i+1), (width//2-p*10*len(str(i+1)), height//2+p*10), cv2.FONT_HERSHEY_DUPLEX, p, (255, 30, 30), p*2)  # Blue number

    raw_img_bytes = img.tobytes()

    return raw_img_bytes


# Build input file input.264 (AVC encoded elementary stream)
################################################################################
process = sp.Popen(f'ffmpeg -y -video_size {width}x{height} -pixel_format bgr24 -f rawvideo -r {fps} -an -sn -dn -i pipe: -f h264 -g 1 -pix_fmt yuv444p -crf 10 -tune zerolatency -an -sn -dn input.264', stdin=sp.PIPE)

#-x264-params aud=1
#Adds [  0,   0,   0,   1,   9,  16 ] to the beginning of each encoded frame
aud_bytes = b'\x00\x00\x00\x01\t\x10'  #Access Unit Delimiter
#process = sp.Popen(f'ffmpeg -y -video_size {width}x{height} -pixel_format bgr24 -f rawvideo -r {fps} -an -sn -dn -i pipe: -f h264 -g 1 -pix_fmt yuv444p -crf 10 -tune zerolatency -x264-params aud=1 -an -sn -dn input.264', stdin=sp.PIPE)

for i in range(n_frames):
    raw_img_bytes = make_raw_frame_as_bytes(i)
    process.stdin.write(raw_img_bytes) # Write raw video frame to input stream of ffmpeg sub-process.

process.stdin.close()
process.wait()
################################################################################

# Execute FFprobe and create JSON file (showing pkt_pos and pkt_size for every encoded frame):
sp.run('ffprobe -print_format json -show_frames input.264', stdout=open('input_probe.json', 'w'))

# Read FFprobe output to dictionary p
with open('input_probe.json') as f:
    p = json.load(f)['frames']


# Input PIPE: H.264 encoded video, output PIPE: decoded video frames in raw BGR video format
process = sp.Popen(f'ffmpeg -probesize 32 -flags low_delay -f h264 -framerate {fps} -an -sn -dn -i pipe: -f rawvideo -s {width}x{height} -pix_fmt bgr24 -an -sn -dn pipe:', stdin=sp.PIPE, stdout=sp.PIPE)

f = open('input.264', 'rb')

process.stdin.write(aud_bytes)  # Write AUD NAL unit before the first encoded frame.

for i in range(n_frames-1):
    # Read H.264 encoded video frame
    h264_frame_bytes = f.read(int(p[i]['pkt_size']))

    process.stdin.write(h264_frame_bytes)
    process.stdin.write(aud_bytes)  # Write AUD NAL unit after the encoded frame.
    process.stdin.flush()

    # Read decoded video frame (in raw video format) from stdout PIPE.
    buffer = process.stdout.read(width*height*3)
    frame = np.frombuffer(buffer, np.uint8).reshape(height, width, 3)

    # Display the decoded video frame
    cv2.imshow('frame', frame)
    cv2.waitKey(1)

# Write last encoded frame
h264_frame_bytes = f.read(int(p[n_frames-1]['pkt_size']))
process.stdin.write(h264_frame_bytes)

f.close()


process.stdin.close()
buffer = process.stdout.read(width*height*3)   # Read the last video frame
process.stdout.close()

# Wait for sub-process to finish
process.wait()

cv2.destroyAllWindows()