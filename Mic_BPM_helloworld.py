from lx16a import *
from math import sin, cos
from aubio import source, tempo
from numpy import median, diff
import numpy
import time
import threading
import pyaudio
import wave


def get_file_bpm(path, params=None):
    """ Calculate the beats per minute (bpm) of a given file.
        path: path to the file
        param: dictionary of parameters
    """
    if params is None:
        params = {}
    # default:
    samplerate, win_s, hop_s = 44100, 1024, 512 #44100*2, 1024*2, 512*2
    if 'mode' in params:
        if params.mode in ['super-fast']:
            # super fast
            samplerate, win_s, hop_s = 4000, 128, 64
        elif params.mode in ['fast']:
            # fast
            samplerate, win_s, hop_s = 8000, 512, 128
        elif params.mode in ['default']:
            pass
        else:
            raise ValueError("unknown mode {:s}".format(params.mode))
    # manual settings
    if 'samplerate' in params:
        samplerate = params.samplerate
    if 'win_s' in params:
        win_s = params.win_s
    if 'hop_s' in params:
        hop_s = params.hop_s

    s = source(path, samplerate, hop_s)
    samplerate = s.samplerate
    o = tempo("specdiff", win_s, hop_s, samplerate)
    # List of beats, in samples
    beats = []
    # Total number of frames read
    total_frames = 0

    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = o.get_last_s()
            beats.append(this_beat)
            #if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
        total_frames += read
        if read < hop_s:
            break

    def beats_to_bpm(beats, path):
        # if enough beats are found, convert to periods then to bpm
        if len(beats) > 1:
            if len(beats) < 4:
                print("few beats found in {:s}".format(path))
            bpms = 60./diff(beats)
            return median(bpms)
        else:
            print("not enough beats found in {:s}".format(path))
            return 0

    return beats_to_bpm(beats, path)

def bpm_every_5_sec():
#     Call this function again in 5 seconds
  threading.Timer(5.0, bpm_every_5_sec).start()  
  
  form_1 = pyaudio.paInt16 # 16-bit resolution
  chans = 1 # 1 channel
  samp_rate = 48000 # 44.1kHz sampling rate
  chunk = 8192 # 2^12 samples for buffer
  record_secs = 5 # seconds to record
  dev_index = 0 # device index found by p.get_device_info_by_index(ii)
  wav_output_filename = 'test1.wav' # name of .wav file

  audio = pyaudio.PyAudio() # create pyaudio instantiation

# create pyaudio stream
  stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
  print("recording")
  frames = []

# loop through stream and append audio chunks to frame array
  for ii in range(0,int((samp_rate/chunk)*record_secs)):
      data = stream.read(chunk)
      frames.append(data)

  print("finished recording")

# stop the stream, close it, and terminate the pyaudio instantiation
  stream.stop_stream()
  stream.close()
  audio.terminate()

# save the audio frames as .wav file
  wavefile = wave.open(wav_output_filename,'wb')
  wavefile.setnchannels(chans)
  wavefile.setsampwidth(audio.get_sample_size(form_1))
  wavefile.setframerate(samp_rate)
  wavefile.writeframes(b''.join(frames))
  wavefile.close()
  for f in args.sources:
        bpm = get_file_bpm(f, params = args)
        print("{:6s} {:s}".format("{:2f}".format(bpm), f))
        print(bpm)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode',
            help="mode [default|fast|super-fast]",
            dest="mode", default='default')
    parser.add_argument('sources',
            nargs='+',
            help="input_files")
    args = parser.parse_args()
    for f in args.sources:
        bpm = get_file_bpm(f, params = args)
        print("{:6s} {:s}".format("{:2f}".format(bpm), f)) 
# This is the port that the controller board is connected to
# This will be different for different computers
# On Windows, try the ports COM1, COM2, COM3, etc...
# On Raspbian, try each port in /dev/
    LX16A.initialize("/dev/ttyUSB0")

# There should two servos connected, with IDs 1 and 2
    servo1 = LX16A(1)
    t = 0
    bpm_every_5_sec()

    while True:
    # Two sine waves out of phase
    # The servos can rotate between 0 and 240 degrees,
    # So we adjust the waves to be in that range
        servo1.moveTimeWrite(sin(t) * 5 + 120)
        t += 0.01
