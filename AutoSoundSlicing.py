import os
import scipy.io.wavfile
import yaml
from pydub import AudioSegment

enumerator = 0 # Global variable

with open('AudioParameters.yaml') as f:
        saved_parameters = yaml.safe_load(f)

SOURCE_FILE_NAME = saved_parameters['SOURCE_FILE_NAME'] # Inputting audio file name mp3 or wav format
SOURCE_FORMAT = saved_parameters['SOURCE_FORMAT'] # May be only mp3 or wav
POSTFIX_NAME = saved_parameters['POSTFIX_NAME'] # Additional name for outputting tracks
OUTPUT_FOLDER_NAME = saved_parameters['OUTPUT_FOLDER_NAME'] # A folder with the specified name will be created for storing outputting tracks
MIN_TRACK_TIME = saved_parameters['MIN_TRACK_TIME'] # Constant of minimum seconds of an outtput track time
MAX_TRACK_TIME = saved_parameters['MAX_TRACK_TIME'] # Constant of maximim output track time
SILENCE_WAVE = saved_parameters['SILENCE_WAVE'] # Constant of silence wave amplitude. May be variable from 0.02 to 0.045

# With inputting mp3 file will convert and save new wav file
if SOURCE_FORMAT == 'mp3':
    sound = AudioSegment.from_mp3(f"{SOURCE_FILE_NAME}.{SOURCE_FORMAT}")
    sound.export(f"{SOURCE_FILE_NAME}.wav", format="wav")

# This function cannot read wav files with 24-bit data.
samplerate, data = scipy.io.wavfile.read(f"{SOURCE_FILE_NAME}.wav") # samplerate - how many samples in 1 second, data - the samples themselves
data = data/abs(data).max()
data = data.astype('float32')

min_silence_time = round(samplerate * 0.2835) # initial time of silence that will cause of slice. May variable from 0.2 to 0.4
long_step = round(samplerate * 0.02267)
short_step = round(samplerate * 0.0002267)
silence_time_increment = round(min_silence_time * 0.02)

if not os.path.isdir(f"{OUTPUT_FOLDER_NAME}"):
 os.mkdir(f"{OUTPUT_FOLDER_NAME}")

def sensor(data, samplerate, min_silence_time):
    # recursive function dividing the source audio file into several small parts

    global enumerator

    if min_silence_time <= samplerate * 0.2:
        enumerator += 1
        scipy.io.wavfile.write(f"{OUTPUT_FOLDER_NAME}/{enumerator}{POSTFIX_NAME}.wav", samplerate, data)
        return
    start = 0
    current_point = samplerate * MIN_TRACK_TIME

    while current_point < data.shape[0] - samplerate * MIN_TRACK_TIME - long_step - short_step:
        current_silence_time = 0
        while True:
            if abs(data[current_point, 0]) <= SILENCE_WAVE:
                current_point += short_step
                current_silence_time += short_step
                if current_silence_time >= min_silence_time:
                    new_data = data[start:current_point, : ]
                    if new_data.shape[0] >= samplerate * (MAX_TRACK_TIME + 1):
                        sensor(new_data, samplerate, min_silence_time - silence_time_increment)
                    else:
                        enumerator += 1
                        scipy.io.wavfile.write(f"{OUTPUT_FOLDER_NAME}/{enumerator}{POSTFIX_NAME}.wav", samplerate, new_data)
                    start = current_point
                    current_point += samplerate * MIN_TRACK_TIME
                    break
            else:
                break
        current_point += long_step
    new_data = data[start:-1, : ]
    if new_data.shape[0] >= samplerate * (MAX_TRACK_TIME + 1) :
        sensor(new_data, samplerate, min_silence_time - silence_time_increment)
    else:
        enumerator += 1
        scipy.io.wavfile.write(f"{OUTPUT_FOLDER_NAME}/{enumerator}{POSTFIX_NAME}.wav", samplerate, new_data)

sensor(data, samplerate, min_silence_time)