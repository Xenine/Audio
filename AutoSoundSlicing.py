import scipy.io.wavfile

enumerator = 0

def main():
	# This function cannot read wav files with 24-bit data.
	samplerate, data = scipy.io.wavfile.read('raw_21m_ru.wav') # samplerate - how many samples in 1 second, data - the samples themselves
	number_of_samples = data.shape[0]
	length = number_of_samples / samplerate
	silence = 700 # silence wave amplitude
	min_silence_len = 12500 # 0.3 second
	

	print(f"length = {length} seconds")
	print(f"samplerate = {samplerate}")
	print(f"data.shape = {number_of_samples}")

	hypersensitivity(data, min_silence_len, silence, samplerate)

def hypersensitivity(data, min_silence_len, silence, samplerate):
	global enumerator
	if min_silence_len <= 8800:
		enumerator += 1
		scipy.io.wavfile.write(f"sounds3/{enumerator}_sample.wav", samplerate, data)
		return
	start = 0
	current_point = samplerate * 5
	

	while current_point < data.shape[0] - samplerate * 5 - 1010:
		current_silence = 0
		while True:
			if abs(data[current_point, 0]) <= silence:
				current_point += 10
				current_silence += 10
				if current_silence == min_silence_len:
					new_data = data[start:current_point, : ]
					if new_data.shape[0] >= samplerate * 16:
						hypersensitivity(new_data, min_silence_len - 250, silence, samplerate)
					else:
						enumerator += 1
						scipy.io.wavfile.write(f"sounds3/{enumerator}_sample.wav", samplerate, new_data)
					start = current_point
					current_point += samplerate * 5
					break
			else:
				break
		current_point += 1000
	new_data = data[start:-1, : ]
	if new_data.shape[0] >= samplerate * 16:
		hypersensitivity(new_data, min_silence_len - 250, silence, samplerate)
	else:
		enumerator += 1
		scipy.io.wavfile.write(f"sounds3/{enumerator}_sample.wav", samplerate, new_data)

if __name__ == '__main__':
	main()