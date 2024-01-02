# Start from the official TensorFlow GPU image
FROM tensorflow/tensorflow:2.4.1-gpu

# Set the working directory in the container
WORKDIR /app

# Install additional dependencies
RUN gpg --keyserver keyserver.ubuntu.com --recv A4B469963BF863CC
RUN gpg --export --armor A4B469963BF863CC | apt-key add -
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages using pip
RUN pip install --no-cache-dir \
    librosa \
    numpy \
    python-dotenv

# Create directories in the container to match your specified paths
RUN mkdir -p /mnt/d/audio/audio-learn/spectrograms/ \
    && mkdir -p /mnt/d/audio/audio-learn/fsdd/ \
    && mkdir -p /mnt/d/audio/looper-1-04-2021

RUN mkdir /data
RUN mkdir /data/spectrograms
RUN mkdir /data/fsdd
RUN mkdir /data/input_files

# Define environment variable for TensorFlow to run with GPU support
ENV TF_FORCE_GPU_ALLOW_GROWTH=true
