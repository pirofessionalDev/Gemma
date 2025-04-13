import os
import datetime
import psutil
import subprocess
import asyncio
import edge_tts
import speech_recognition as sr
import pygame
import json
import threading
import time
import random
from vosk import Model, KaldiRecognizer
import wave
import pyaudio

# Global mute flag
mute_flag = False

# Load the custom profile
def load_profile():
    try:
        with open("custom.json", "r") as file:
            return json.load(file)
    except Exception:
        return {}

# Initialize Pygame mixer
pygame.mixer.init()

# Speak using Edge TTS and pygame
async def speak_async(text):
    if mute_flag:  # Don't speak if mute is enabled
        return

    if not text.strip():
        return

    filename = "response.mp3"

    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()

        if os.path.exists(filename):
            try:
                os.remove(filename)
            except PermissionError:
                await asyncio.sleep(0.5)
                os.remove(filename)

        communicate = edge_tts.Communicate(text, voice="en-GB-SoniaNeural")
        await communicate.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.unload()

    except Exception as e:
        print(f"[TTS Error]: {e}")

def speak(text):
    asyncio.run(speak_async(text))

# Voice to text
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("I am Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio)
            print(f"You: {query}")
            return query
        except sr.WaitTimeoutError:
            speak("No input detected, Sir.")
        except sr.UnknownValueError:
            speak("Sorry Sir, I didn't catch that.")
        except sr.RequestError:
            speak("I’m having trouble reaching the speech service.")
        except Exception as e:
            speak("Something went wrong.")
            print(f"[Voice Error]: {e}")
    return ""

# Time greeting
def get_time_greetings():
    hour = datetime.datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

# Local system commands
def perform_local_command(command):
    command = command.lower()

    if "open firefox" in command:
        os.system("start firefox")
        return "Launching Firefox, Sir."

    elif "open chrome" in command:
        os.system("start chrome")
        return "Launching Chrome, Sir."

    elif "battery" in command:
        battery = psutil.sensors_battery()
        if battery:
            return f"Battery is at {battery.percent}% and {'charging' if battery.power_plugged else 'not charging'}."
        else:
            return "I can't read the battery status right now."

    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"It is currently {now}."

    elif "shutdown" in command:
        os.system("shutdown /s /t 1")
        return "Shutting down, Sir."

    return None

# Hourly alert messages
hourly_quotes = [
    "Sir, your brain needs fuel. Drink some water.",
    "Stretch like you're reaching for that last slice of pizza!",
    "Don't make me come over there and force a break on you.",
    "You’ve been working for an hour. I’m proud. Now move!",
    "I’m not nagging, I’m caring—hydrate!",
    "Time to stand up, do a victory dance, or just stretch.",
    "A break a day keeps burnout away. Trust me, I'm a genius.",
    "Thursday reminds you: chairs are not beds.",
    "Another hour, another opportunity to hydrate.",
    "If I could walk, I’d be pacing. You should too.",
    "Don't make me hack into your Spotify to play dance music.",
    "Remember: even Iron Man took breaks. Now move it!"
]

wake_responses = [
    "Yes Sir?",
    "Listening...",
    "At your service.",
    "What’s up, boss?",
    "Hola Señor, how can I help?",
    "I’m awake, don’t worry.",
    "Reporting for duty!",
    "Ready when you are, Sir.",
]

def is_pycharm_running():
    for process in psutil.process_iter(['name']):
        if process.info['name'] and "pycharm" in process.info['name'].lower():
            return True
    return False

# Background alert loop
def hourly_alerts_when_pycharm_active():
    print("Thursday: Monitoring PyCharm for hourly alerts...")
    alerted_time = None

    while True:
        if is_pycharm_running():
            current_time = time.localtime()
            if alerted_time != current_time.tm_hour:
                message = random.choice(hourly_quotes)
                print("Thursday (alert):", message)
                speak(message)
                alerted_time = current_time.tm_hour
        time.sleep(30)

# Wake word listener with 10 seconds listening period
def listen_for_wake_word():
    model = Model("vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, 16000)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Thursday is waiting for the wake word...")

    listening_time = 10  # Seconds of listening after wake word detection
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if 'text' in result and ("hey thursday" in result['text'].lower() or "hey" in result['text'].lower()):
                print("Wake word detected! Listening for next 10 seconds...")
                start_time = time.time()

                # Listen for 10 seconds after wake word is detected
                user_input = ""
                while time.time() - start_time < listening_time:
                    data = stream.read(4096, exception_on_overflow=False)
                    if rec.AcceptWaveform(data):
                        result = json.loads(rec.Result())
                        if 'text' in result:
                            print(f"Received input during listening period: {result['text']}")
                            user_input = result['text']
                            break

                print("Listening period is over. Going back to sleep.")
                if user_input:
                    return user_input

# Mute control
def mute_functionality(user_input):
    global mute_flag
    if "mute" in user_input.lower():
        mute_flag = True
        speak("Mute activated, Sir.")
    elif "unmute" in user_input.lower():
        mute_flag = False
        speak("Unmute activated, Sir.")

# Main AI assistant loop
def chat_with_thursday():
    profile = load_profile()
    name = profile.get("name", "Sir")

    speak("Hello, I'm Thursday, your personal AI assistant.")

    while True:
        user_input = listen_for_wake_word()

        # Randomized wake response
        speak(random.choice(wake_responses))

        if not user_input:
            continue

        user_input = user_input.lower()

        if user_input in ['exit', 'quit', '221']:
            goodbye = "Goodbye Sir."
            print("Thursday:", goodbye)
            speak(goodbye)
            break

        # Mute command check
        mute_functionality(user_input)

        # Greeting triggers
        if any(greet in user_input for greet in ["hi", "hey", "hello", "yo"]):
            time_greeting = get_time_greetings()
            greet_text = f"Hello {name}, {time_greeting}!"
            print("Thursday:", greet_text)
            speak(greet_text)
            continue

        # Custom triggers
        if "what is your name" in user_input or "who are you" in user_input:
            speak("I am Thursday, your personal assistant.")
            continue

        elif "my name" in user_input:
            if name:
                speak(f"Your name is {name}, Sir.")
            else:
                speak("I don't know your name yet, Sir.")
            continue

        elif "love of my life" in user_input:
            love = profile.get("love", "I don't know who the love of your life is yet, Sir.")
            speak(f"The love of your life is {love}, Sir.")
            continue

        elif "good night" in user_input:
            speak("Good night, Sir.")
            continue

        elif "Who is your master" in user_input or "who created you" in user_input:
            speak("My creator is Rohit.")
            continue

        # Local commands
        local_response = perform_local_command(user_input)
        if local_response:
            print("Thursday:", local_response)
            speak(local_response)
            continue

        # LLM fallback (Gemma).
        result = subprocess.run(
            ["ollama", "run", "dolphin-phi"],
            input=user_input.encode(),
            stdout=subprocess.PIPE
        )
        response = result.stdout.decode().strip()
        print("Thursday:", response)
        speak(response)

# === Entry point ===
if __name__ == "__main__":
    alert_thread = threading.Thread(target=hourly_alerts_when_pycharm_active, daemon=True)
    alert_thread.start()

    chat_with_thursday()
