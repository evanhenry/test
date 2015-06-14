#audio libraries
from matplotlib.mlab import find
from matplotlib import pyplot as plt
import pyaudio
import numpy as np
import math
  
# Node
class HiveNode:

	## Initialize
	def __init__(self, config=None):
		# Configuration
		if not config:
			self.MICROPHONE_CHANNELS = 1
			self.MICROPHONE_RATE = 44100
			self.MICROPHONE_CHUNK = 4096
			self.MICROPHONE_FORMAT = 8
			self.MICROPHONE_RECORD_SECONDS = 2
			self.MICROPHONE_LOWPASS = 1000 # hz
			
		# Initializers
		try:
			self.init_mic()
		except Exception as e:
			print str(e)

	## Initialize audio
	def init_mic(self):
		""" part of revised code for audio processing """
		# Start audio stream
		try:
			self.p = pyaudio.PyAudio()
			self.microphone = self.p.open(
				format=pyaudio.paInt16,
				channels=self.MICROPHONE_CHANNELS,
				rate=self.MICROPHONE_RATE,
				input=True,
				frames_per_buffer=self.MICROPHONE_CHUNK)
		except Exception as e:
			raise e
			
	## Close Microphone
	def close_mic(self):
		"""cleanly back out and release sound card."""
		self.p.close(self.microphone)
	
	# Capture Audio
	def capture_audio(self, trimBy=10):
		db = None
		hz = None
		try:
			# Capture Audio and convert to numeric
			audio = [] 
			for i in range(0, self.MICROPHONE_RATE / self.MICROPHONE_CHUNK * self.MICROPHONE_RECORD_SECONDS):
				audioString = self.microphone.read(self.MICROPHONE_CHUNK)
				audioNumeric = np.fromstring(audioString,dtype=np.int16)
				audio.append(audioNumeric)
			
			# Calculate Pitch
			pitch = []
			for signal in audio:
				crossing = [math.copysign(1.0, s) for s in signal]
				index = find(np.diff(crossing));
				f0 = round(len(index) * self.MICROPHONE_RATE /(2.0 * np.prod(len(signal))))
				pitch.append(f0)
			pitch = np.array(pitch)
			pitch_lowpass = pitch[pitch < self.MICROPHONE_LOWPASS]
			hz = np.median(pitch_lowpass)
			
			# Calculate Decibels
			# audio.flatten() # pull data from record() thread
			left,right=np.split(np.abs(np.fft.fft(audio)),2)
			db = np.add(left,right[::-1])
			db = np.multiply(20,np.log10(db)) # db
			db = np.mean(np.multiply(20,np.log10(db))) # convert to dB
		except Exception as error:
			self.log_msg('MIC', 'Error: %s' % str(error))
		return { "db" : db, "hz" : hz}
		
	def log_msg(self, a, b):
		print a,b
if __name__ == '__main__':
	app = HiveNode()
	app.capture_audio()