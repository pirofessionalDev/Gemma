import os
import datetime
import psutil
import subprocess
import asyncio
import edge_tts
import speech_recognition as sr
import pygame
import json

# Load the custom profile
def load_profile():
    try:
        with open("custom.json", "r") as file:
            return json.load(file)
    except Exception:
        return {}

# Initialize Pygame mixer
pygame.mixer.init()

# Speak function using Edge TTS and pygame
async def speak_async(text):
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
                print("Waiting for file to be released...")
                await asyncio.sleep(0.5)
                try:
                    os.remove(filename)
                except Exception as e:
                    print(f"Could not delete old response.mp3: {e}")
                    return

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

# Convert speech to text
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

# Local commands
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

# Chat loop
def chat_with_gemma():
    profile = load_profile()

    greeting = "Are we working on a project, are we Sir?"
    print("Gemma:", greeting)
    speak(greeting)

    while True:
        try:
            user_input = get_voice_input()
            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit']:
                goodbye = "Goodbye Sir."
                print("Gemma:", goodbye)
                speak(goodbye)
                break

            # Custom questions
            if "your name" in user_input.lower():
                speak("I am Gemma, your personal assistant.")
                continue
            elif "my name" in user_input.lower():
                name = profile.get("name", None)
                if name:
                    speak(f"Your name is {name}, Sir.")
                else:
                    speak("I don't know your name yet, Sir.")
                continue
            elif "love of my life" in user_input.lower():
                love = profile.get("love", "I don't know who the love of your life is yet, Sir.")
                speak(f"The love of your life is {love}, Sir.")
                continue
            local_response = perform_local_command(user_input)
            if local_response:
                print("Gemma:", local_response)
                speak(local_response)
                continue

            result = subprocess.run(
                ["ollama", "run", "gemma:2b"],
                input=user_input.encode(),
                stdout=subprocess.PIPE
            )
            response = result.stdout.decode().strip()
            print("Gemma:", response)
            speak(response)

        except KeyboardInterrupt:
            print("\nGemma: Interrupted. Goodbye Sir.")
            speak("Interrupted. Goodbye Sir.")
            break

if __name__ == "__main__":
    chat_with_gemma()
