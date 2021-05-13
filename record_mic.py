import pyaudio
import wave
from threading import Thread 
import time
import sys

TRACK_COUNT_FILE = 'track_count.txt'
RECORD_SECONDS = 5

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
			try:
				end = data[0]
			except IndexError as e:
				return

	def close(self):
		""" Graceful shutdown """ 
		self.stream.close()
		self.p.terminate()

def main():
	if 'play' in sys.argv:
		play_tracks(sys.argv[2:])	
	elif 'special' in sys.argv:
		play_tracks_special()
	else:
		record_and_play(3)


def record_and_play(n):
	'''
	Waits three seconds before and between each track recording
	plays previous tracks while recording next tracks
	'''
	track_files = []
	for i in range(n):
		print(f'Recording track #{i+1}:')
		for j in range(3):
			print(3-j, end = '\r')
			time.sleep(1)
		if track_files:
			for track in track_files:
				play(AudioFile(track))
		#TODO: ask whether to redo recording here
		track_files.append(record_mic_to_file(f'track__{i}.wav', False))

	print('Done recording. Engaging harmonic replay...')
	for j in range(3):
		print(f'In {3-j}...', end = '\r')
		time.sleep(1)
	
	print('Playing...')
	threads = []
	for track in track_files:
		threads.append(play(AudioFile(track)))

	wait(RECORD_SECONDS)
	print('Done.')


def add_tracks(num_tracks):
	track_count = get_track_count()
	new_track_id = f'track_{track_count+1}.wav'


def get_track_count():
	global TRACK_COUNT_FILE
	with open(TRACK_COUNT_FILE, 'r') as f:
		return f.readline().strip()


def update_track_count(n):
	global TRACK_COUNT_FILE
	with open(TRACK_COUNT_FILE, 'w') as f:
		f.write(str(n))


def play_tracks(tracks):
	print(f'Playing track {tracks}' )
	track_files = ['track__0.wav', 'track__1.wav', 'track__2.wav']
	for i in tracks:
		play(AudioFile(track_files[int(i)-1]))
	wait(RECORD_SECONDS)
	print('Done.')



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
	global RECORD_SECONDS 
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
		print(int( (i % int(RATE / CHUNK * RECORD_SECONDS)/RATE)*CHUNK), end = '\r' )
		data = stream.read(CHUNK)
		frames.append(data)
	print()
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

	if input('Are you happy with that recording? [Y]/N: ').lower() in ['n', 'no']:
		print(f'Rerecording...')
		for j in range(3):
			print(3-j, end = '\r')
			time.sleep(1)
		return record_mic_to_file(filename, choose_mic)
	else:
		return filename


def wait(n):
	for i in range(n):
		time.sleep(1)


def main_old():
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

def play_tracks_special():
	print(f'Hello' )
	track_files = ['special/track_0.wav', 'special/track_1.wav', 'special/track_2.wav']
	for i in track_files:
		play(AudioFile(i))
	wait(RECORD_SECONDS)
	print('Done')


if __name__ == '__main__': #Call main() unless this file is being imported elsewhere
	main()
