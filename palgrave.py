import json
from pathlib import Path
import random
import sys
import time
import requests
import webbrowser
import urllib.parse
from spotify_local import SpotifyLocal

import pyaudio
import sounddevice
import vosk

MODEL = "vosk-model-small-en-us-0.15"
AUDIO_BITRATE = 44100
AUDIO_BUFFER = 1024

ENABLE_VOSK_DEBUG = False


class SpeakOutput():
	def __init__(self):
		# requires that you install pyttsx3
		try:
			import pyttsx3
		except ImportError:
			raise Exception("Please pip install pyttsx3")
		engine = pyttsx3.init()
		engine.setProperty("rate", 130) # words per minute
		engine.setProperty("volume", 1.0)
		#voices = engine.getProperty("voices")
		#for i, voice in enumerate(voices):
		#	print("{}: age: {} gender: {} id: {} languages: {} name: {}".format(
		#		i,
		#		voice.age,
		#		voice.gender,
		#		voice.id,
		#		voice.languages,
		#		voice.name,
		#	))
		engine.setProperty("voice", "english-north")
		self.engine = engine

	def callback_output_text(self, text):
		self.engine.say(text)
		self.engine.runAndWait()


class PrintOutput():
	def __init__(self):
		pass

	def callback_output_text(self, text):
		print(text)


class BaseRobot():
	def __init__(self, output):
		self.output = output
		self.setup()

	def setup(self):
		pass

	def respond(self, text):
		self.output.callback_output_text(text)


class EchoImplementation(BaseRobot):
	"""
	Annoying bot that just repeats what you say.
	"""
	def callback_receive_text(self, text):
		self.respond(text)


class ReverseImplementation(BaseRobot):
	"""
	Bot that reverses what it hears:
	"Hi how are you" -> "you are how hi"
	"""
	def callback_receive_text(self, text):
		words = text.split()
		reversed_words = " ".join(reversed(words))
		self.respond(reversed_words)


class BackwardsImplementation(BaseRobot):
	"""
	Bot that repeats you but backwards:
	"Hi how are you" -> "uoy era woh ih"
	"""
	def callback_receive_text(self, text):
		self.respond(text[::-1])


class PalgraveImplementation(BaseRobot):
	"""
	The best bot
	"""

	def setup(self):
		self.mode = None

	def callback_receive_text(self, text):
		if self.mode == "awaitingSearch":
			webbrowser.open("https://duckduckgo.com/?q=" + urllib.parse.quote(text))
			self.respond("Opening web browser")
			self.mode = None
			return
		if self.mode == "awaitingNote":
			notes = open("palgravenotes","a")
			notes.write(text)
			self.respond("Note saved successfully!")
			self.mode = None
			return

		if "palgrave" in text:
			self.respond("Hello!")
		if "i" in text and "bored" in text and not "not" in text:
			randomnumber = random.random()
			if randomnumber < 0.5:
				self.respond("Do a jigsaw")
			else:
				self.respond("Listen to music")
		if "exit" in text or "quit" in text and not "don't" in text and not "do not" in text:
			self.respond("Goodbye!")
			time.sleep(2)
			quit()
		if "get" in text and "hypertext" in text:
			self.respond("Please type a URL")
			getURL = input("URL: ")
			getresponse = requests.get(getURL)
			print("Response: ")
			print(getresponse)
			print(getresponse.text)
			self.respond("Do you want to open this url in your web browser? Type y or n")
			openInWebbrowser = input("Open in web browser? y/n")
			if openInWebbrowser == "y":
				webbrowser.open(getURL)
			elif openInWebbrowser == "n":
				self.respond("OK")
			else:
				self.respond("I didn't receive y or n, so I didn't open the browser")
		if "thanks" in text or "thank you" in text:
			self.respond("No problem")
		if "search" in text:
			self.respond("What would you like to search?")
			self.mode = "awaitingSearch"
			return
		if "what" in text and "you" in text and "do" in text:
			self.respond("I can do many things.")
			x = random.random()
			if x < 0.5:
				time.sleep(0.6)
				self.respond("You can say, open website or search")
			elif x > 0.5:
				time.sleep(0.6)
				self.respond("You can say, thanks or i'm bored")
			else:
				self.respond("Sorry, an error occurred at line 132 approximately. I will send you to the link to report a bug.")
				webbrowser.open("https://github.com/kaiete/InstantPalgrave/issues")
		if "open" in text and "website" in text:
			self.respond("Please type a URL")
			webbrowser.open(input("URL: "))
		if "spotify" in text and "pause" in text:
			with SpotifyLocal() as s:
				s.pause()
			self.respond("Paused")
		if "note" in text and "save" in text:
			self.respond("Please say a note")
			self.mode = "awaitingNote"
			return


def get_recognizer():
	if not Path(MODEL).exists():
		raise Exception("Model {} doesn't exist, maybe download it from: https://alphacephei.com/vosk/models and unzip it here".format(MODEL))
	if not ENABLE_VOSK_DEBUG:
		vosk.SetLogLevel(-1)
	vosk_model = vosk.Model(MODEL)
	rec = vosk.KaldiRecognizer(vosk_model, AUDIO_BITRATE)
	return rec


def get_audio_stream():
	audio = pyaudio.PyAudio()
	stream = audio.open(
		format = pyaudio.paInt16,
		channels = 1,
		rate = AUDIO_BITRATE,
		input = True,
		frames_per_buffer = AUDIO_BUFFER,
	)
	return stream


def main(bot_mode):
	recognizer = get_recognizer()
	stream = get_audio_stream()
	#output = PrintOutput()
	output = SpeakOutput()
	if bot_mode == "palgrave":
		robot = PalgraveImplementation(output=output)
	elif bot_mode == "echo":
		robot = EchoImplementation(output=output)
	elif bot_mode == "reverse":
		robot = ReverseImplementation(output=output)
	elif bot_mode == "backwards":
		robot = BackwardsImplementation(output=output)
	else:
		raise Exception("Unknown bot mode: {}".format(bot_mode))
	while 1:
		data = stream.read(AUDIO_BUFFER)
		if recognizer.AcceptWaveform(data):
			raw_result = recognizer.Result()
			result = json.loads(raw_result)
			text = result.get("text")
			if text:
				print("I heard: {}".format(text))
				stream.stop_stream()
				robot.callback_receive_text(text)
				stream.start_stream()


if __name__ == "__main__":
	if len(sys.argv) > 1:
		bot_mode = sys.argv[1]
	else:
		bot_mode = "palgrave"
	main(bot_mode)
