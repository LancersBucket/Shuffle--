# Shuffle--

> A simple, pure shuffling music player

## Table of Contents
+ [About](#about)
+ [Getting Started](#getting-started)
+ [Developing](#developing)
+ [Usage](#usage)

## About
Shuffle-- is designed to be a simple music player to shuffle your music made with PyQT5 with yt-dlp integration to download files from a playlist.

## Getting Started
To download Shuffle--, go to the releases page and download the latest version of smm.exe. The first time you run it, a music folder and a config.ini file will be generated. Then, you can add the music files you'd like in the music folder, and enable yt-dlp playlist mirroring in the config file.

## Developing
### Prerequisites
- Python 3.11

### Running
Step 1: Clone the repository
```
git clone https://github.com/LancersBucket/Shuffle--.git
```
Step 2: Download the dependencies
```
pip install -r requirements.txt
```
Step 3: Run the program
```
python smm.py
```

## Usage
Upon opening the program, it will first attempt to shuffle the songs found in the music subdirectory. Pressing the shuffle button will reload the queue and add or remove any changed files.