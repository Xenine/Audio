import scipy.io.wavfile

# This function cannot read wav files with 24-bit data.
samplerate, data = scipy.io.wavfile.read('raw_45m.wav') 

print(f"number of channels = {data.shape[1]}")
length = data.shape[0] / samplerate
print(f"length = {length}s")
print(f"samplerate = {samplerate}")
print(f"data.shape = {data.shape}")

new_data = []
min_silence_len = 12500 # 0.3 sec
silence = 700 # Амплитуда волны 
current = 0
i = 44100 * 5
dot = 0
count = 0

while i < data.shape[0] - 1 - min_silence_len:
	if abs(data[i, 0] < silence):
		for current in range(0, min_silence_len, 10):
			if abs(data[i + current + 10, 0]) < silence:
				pass
			else:
				i += current
				break
			if current == min_silence_len - 10:
				i += current
				new_data = data[dot:i, :]
				count += 1
				scipy.io.wavfile.write(f"sounds2/{count}_45m.wav", samplerate, new_data)
				dot = i
				i += 44100 * 5 # 5 sec skip
	i += 100