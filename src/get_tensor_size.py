import math

FRAME_SIZE = 512
HOP_LENGTH = 256
DURATION = 10.025  # in seconds
SAMPLE_RATE = 22050
n_bins = FRAME_SIZE // 2 + 1
n_frames = math.ceil((DURATION * SAMPLE_RATE) / HOP_LENGTH)
print((n_bins, n_frames))