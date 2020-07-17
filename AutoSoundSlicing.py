import os
import scipy.io.wavfile
import yaml
from pydub import AudioSegment

enumerator = 0 # Global variable

with open('AudioParameters.yaml') as f:
        saved_parameters = yaml.safe_load(f)

SOURCE_FILE_NAME = saved_parameters['SOURCE_FILE_NAME']
SOURCE_FORMAT = saved_parameters['SOURCE_FORMAT']
POSTFIX_NAME = saved_parameters['POSTFIX_NAME']
OUTPUT_FOLDER_NAME = saved_parameters['OUTPUT_FOLDER_NAME']
MIN_TRACK_TIME = saved_parameters['MIN_TRACK_TIME'] # Constant of minimum seconds of an output {OUTPUT_FOLDER_NAME}
MAX_TRACK_TIME = saved_parameters['MAX_TRACK_TIME'] # Constant of maximim output track time
SILENCE_WAVE = saved_parameters['SILENCE_WAVE'] # Constant of silence wave amplitude


def main():
    if SOURCE_FORMAT == 'mp3':
        sound = AudioSegment.from_mp3(f"{SOURCE_FILE_NAME}.{SOURCE_FORMAT}")
        sound.export(f"{SOURCE_FILE_NAME}.wav", format="wav")

    # This function cannot read wav files with 24-bit data.
    samplerate, data = scipy.io.wavfile.read(f"{SOURCE_FILE_NAME}.wav") # samplerate - how many samples in 1 second, data - the samples themselves

    if not os.path.isdir(f"{OUTPUT_FOLDER_NAME}"):
     os.mkdir(f"{OUTPUT_FOLDER_NAME}")
    
    min_silence_time = 12500 # 0.3 second
    
    sensor(data, min_silence_time, samplerate)

def sensor(data, min_silence_time, samplerate):
    global enumerator

    if min_silence_time <= 8750:
        enumerator += 1
        scipy.io.wavfile.write(f"{OUTPUT_FOLDER_NAME}/{enumerator}{POSTFIX_NAME}.wav", samplerate, data)
        return
    start = 0
    current_point = samplerate * MIN_TRACK_TIME
    

    while current_point < data.shape[0] - samplerate * MIN_TRACK_TIME - 1010:
        current_silence_time = 0
        while True:
            if abs(data[current_point, 0]) <= SILENCE_WAVE:
                current_point += 10
                current_silence_time += 10
                if current_silence_time == min_silence_time:
                    new_data = data[start:current_point, : ]
                    if new_data.shape[0] >= samplerate * (MAX_TRACK_TIME + 1):
                        sensor(new_data, min_silence_time - 250, samplerate)
                    else:
                        enumerator += 1
                        scipy.io.wavfile.write(f"{OUTPUT_FOLDER_NAME}/{enumerator}{POSTFIX_NAME}.wav", samplerate, new_data)
                    start = current_point
                    current_point += samplerate * MIN_TRACK_TIME
                    break
            else:
                break
        current_point += 1000
    new_data = data[start:-1, : ]
    if new_data.shape[0] >= samplerate * (MAX_TRACK_TIME + 1) :
        sensor(new_data, min_silence_time - 250, samplerate)
    else:
        enumerator += 1
        scipy.io.wavfile.write(f"{OUTPUT_FOLDER_NAME}/{enumerator}{POSTFIX_NAME}.wav", samplerate, new_data)

if __name__ == '__main__':
    main()