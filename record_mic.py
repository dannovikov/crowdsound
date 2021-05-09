import pyaudio
import wave
from threading import Thread 
import time

class AudioFile:
	# https://stackoverflow.com/a/6951154
    chunk = 1024

    def __init__(self, file):
        """ Init audio stream """ 
        self.wf = wave.open(file, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )

    def play(self):
        """ Play entire file """
        data = self.wf.readframes(self.chunk)
        while data != '':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)

    def close(self):
        """ Graceful shutdown """ 
        self.stream.close()
        self.p.terminate()

def main():
	#Record Tracks from Microphone
	print("Recording track 1")
	t1_file = record_mic_to_file('track1.wav', True)
	print("Recording track 2")
	t2_file = record_mic_to_file('track2.wav', False)

	#play two tracks back at the same time
	t1 = AudioFile(t1_file)
	t2 = AudioFile(t2_file)

	t1_thread, t2_thread = play(t1), play(t2)

	for i in range(3):
		time.sleep(1)
	#ERROR: These threads dont die!!!
	print('done')
	


def play(A):
	'''
	plays an AudioFile object "A"
	'''
	song_thread = Thread(target = A.play)
	assert not song_thread.is_alive()
	song_thread.start()
	return song_thread

def record_mic_to_file(filename, choose_mic = False):
	# https://stackoverflow.com/questions/40704026/voice-recording-using-pyaudio
	CHUNK = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	RECORD_SECONDS = 5
	WAVE_OUTPUT_FILENAME = filename

	p = pyaudio.PyAudio()

	if choose_mic:
		print("----------------------record device list---------------------")
		info = p.get_host_api_info_by_index(0)
		numdevices = info.get('deviceCount')
		for i in range(0, numdevices):
		        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
		            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))

		print("-------------------------------------------------------------")

		mic_index = int(input())
		print("recording via index "+str(mic_index))
	else:
		mic_index = 1

	stream = p.open(format=FORMAT,
	                channels=CHANNELS,
	                rate=RATE,
	                input=True,
	                input_device_index = mic_index,
	                frames_per_buffer=CHUNK)

	print("* recording")

	frames = []

	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
	    data = stream.read(CHUNK)
	    frames.append(data)

	print("* done recording")

	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))
	wf.close()
	return filename




if __name__ == '__main__':
	main()
