# Fat list of imports
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QStatusBar, QSlider
from PyQt5.QtCore import QTimer, QRunnable, QThreadPool
from PyQt5.QtGui import QIcon
from pygame import mixer
from PyQt5 import uic
import sys, os, random, configparser, yt_dlp

# Sets up the config file and reads and/or writes the file depending on if it exists
config = configparser.ConfigParser()
config['yt-dlp'] = {'Playlist Mirroring': 'False',
					'Playlist URL': 'https://www.youtube.com/playlist?list=PLddJoGM8SQ49JKhX2KXcTVvsXO0-_xTOm'
					}

if (not os.path.isfile('config.ini')):
	with open('config.ini', 'w') as configfile:
		config.write(configfile)
		configfile.close()
else:
	config.read('config.ini')

# Class for the ytdlp integration (needs to be sepperated because it will be threaded)
class Worker(QRunnable):
	def run(self):
		# Grabs the URLs to download from the config
		URLS = [config['yt-dlp']['Playlist URL']]
		# Logger class to print what ytdlp is doing
		class MyLogger():			
			def debug(self, msg):
				# For compatibility with youtube-dl, both debug and info are passed into debug
				# You can distinguish them by the prefix '[debug] '
				if msg.startswith('[debug] '):
					pass
				else:
					self.info(msg)

			def info(self, msg):
				print(msg)

			def warning(self, msg):
				print(msg)

			def error(self, msg):
				print(msg)

		# See "progress_hooks" in help(yt_dlp.YoutubeDL)
		# Black magic
		def my_hook(d):
			if d['status'] == 'finished':
				print('Done downloading, now post-processing ...')

		# ytdlp options
		ydl_opts = {
			'logger': MyLogger(),
			'progress_hooks': [my_hook],
			'format': 'ba',
			'outtmpl': 'music/%(title)s [%(id)s].%(ext)s',
			'download_archive': 'archive.txt',
			'ignoreerrors': "only_download",
			'postprocessors': [{
				'key': 'FFmpegExtractAudio',
				'preferredcodec': 'mp3'
			}]
		}

		# runs ytdlp
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			ydl.download(URLS)

# The main UI class
class Ui(QMainWindow):
	queue = []
	currentPos = 0
	playing = False
	paused = False

	def __init__(self):
		super(Ui, self).__init__() # Call the inherited classes __init__ method

		# Sets up multithreading
		self.threadpool = QThreadPool()
		print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

		# Inits music player
		mixer.init()
		
		# Loads files into the queue
		if (not os.path.isdir('music')):
			os.mkdir('music')
		songs = os.listdir('music')
		for song in songs:
			if (song.endswith(".mp3")):
				self.queue.append(song)

		# Shuffles the queue
		Ui.shuffle(self.queue)

		# Loads the predefined ui file from Qt Designer
		uic.loadUi('untitled.ui', self)
		
		# Configure the hooks for the buttons/sliders/Status bar
		self.playPause = self.findChild(QPushButton, 'PlayPause')
		self.playPause.clicked.connect(self.playPauseButton)

		self.back = self.findChild(QPushButton, 'Back')
		self.back.clicked.connect(self.backButton)

		self.forward = self.findChild(QPushButton, 'Forward')
		self.forward.clicked.connect(self.forwardButton)

		self.shufflebut = self.findChild(QPushButton, 'Shuffle')
		self.shufflebut.clicked.connect(self.shuffleButton)

		self.vol = self.findChild(QSlider, 'Volume')
		self.vol.valueChanged.connect(self.volChange)

		self.status = self.findChild(QStatusBar, 'statusbar')

		# Shows the ready message, and an error if there is an error
		self.status.showMessage("Ready. Queued " + str(len(self.queue)) + " songs.")
		if (self.queue == []):
			self.status.showMessage("Error: No files found", 1000)

		# Sets up a pseudo thread to keep track of if a song is finished 
		self.timer = QTimer(self)
		self.timer.setSingleShot(False)
		self.timer.setInterval(1)
		self.timer.timeout.connect(self.loop)
		self.timer.start()

		# Sets the window icon
		self.setWindowIcon(QIcon("3580329.png"))

		# Shows the GUI
		self.show()
		
		# Starts the yt-dlp thread if it is set to True in the config
		if (config['yt-dlp']['Playlist Mirroring'] == 'True'):
			self.threadpool = QThreadPool()
			worker = Worker()
			self.threadpool.start(worker)

	# Helper function to shuffle the queue	
	def shuffle(array):
		array = random.shuffle(array)

	def playsong(self):
		# Gets the name of the file in the queue displays what is currently playing
		name = self.queue[self.currentPos]
		self.status.showMessage("[" + str(self.currentPos+1)+"/"+str(len(self.queue))+"] " + name[0:-4])

		# Loads the music and plays it
		mixer.music.load('music/'+name)
		mixer.music.play()
		mixer.music.set_volume(self.vol.value()/100)

	# Handles pausing and playing. Don't question it. I had to do it this way. I hope.
	def playPauseButton(self):
		if not self.playing:
			self.playing = True
			if (self.paused):
				mixer.music.unpause()
				name = self.queue[self.currentPos]
				self.status.showMessage("[" + str(self.currentPos+1)+"/"+str(len(self.queue))+"] " + name[0:-4])
				self.paused = False
			else:
				self.playsong()
			self.playPause.__setattr__("text","Pause")
		else:
			self.playing = False
			self.paused = True
			mixer.music.pause()
			self.playPause.__setattr__("text","Play")
			self.status.showMessage("Paused")

	# Decrements the queue position
	def backButton(self):
		mixer.music.stop()
		if (self.currentPos < 0):
			self.currentPos = len(self.queue)
		else:
			self.currentPos -= 1
		self.playsong()

	# Increments the queue position
	def forwardButton(self):
		if (self.currentPos >= len(self.queue)-1):
			mixer.music.stop()
			Ui.shuffle(self.queue)
			self.currentPos = 0
		else:
			self.currentPos += 1
		self.playsong()

	# Monitors volume change
	def volChange(self):
		mixer.music.set_volume(self.vol.value()/100)

	# Reloads the queue and shuffles it
	def shuffleButton(self):
		mixer.music.stop()

		self.queue = []
		songs = os.listdir('music')
		for song in songs:
			if (song.endswith(".mp3")):
				self.queue.append(song)

		Ui.shuffle(self.queue)
		self.currentPos = 0
		self.playsong()

	# Checks if music is currently playing and is supposed to be and changes the song if it is stopped
	def loop(self):
		if (self.playing == True and not mixer.music.get_busy()):
			mixer.music.stop()
			self.forwardButton()

# Creates an instance of QtWidgets.QApplication
app = QApplication(sys.argv)
app.setWindowIcon(QIcon('3580329.png'))
# Creates an instance of our class
window = Ui()
# Starts the application
app.exec_()