import os
import datetime
import psutil
import platform
import requests

# --- Local commands like open apps, check battery, etc. ---
def perform_local_command(command):
    command = command.lower()

    if "open firefox" in command:
        if platform.system() == "Windows":
            os.system("start firefox")
        else:
            os.system("firefox &")
        return "Launching Firefox, Sir."

    elif "battery" in command:
        battery = psutil.sensors_battery()
        if battery:
            return f"Battery is at {battery.percent}% and {'charging' if battery.power_plugged else 'not charging'}."
        else:
            return "I can't read the battery status right now."

    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"It is currently {now}, Sir."

    elif "shutdown" in command:
        if platform.system() == "Windows":
            os.system("shutdown /s /t 0")
        else:
            os.system("shutdown now")
        return "Shutting down, Sir."

    return None  # Not a local command


# --- Interact with Gemma via Ollama API ---
def ask_gemma(prompt):
    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "gemma:2b",
            "prompt": prompt,
            "stream": False
        })
        return response.json().get("response", "Gemma didn't respond, Sir.")
    except Exception as e:
        return f"Failed to reach Gemma: {e}"


# --- Live Assistant Loop ---
def chat_with_gemma():
    print("Gemma: Greetings Sir. Working on a project, are we Sir?\n")

    while True:
        try:
            user_input = input("You: ")

            if user_input.lower() in ['exit', 'quit']:
                print("Gemma: Goodbye, Sir.")
                break

            # Check if it's a local command
            local_response = perform_local_command(user_input)
            if local_response:
                print("Gemma:", local_response)
                continue

            # Else ask Gemma
            response = ask_gemma(user_input)
            print("Gemma:", response)

        except KeyboardInterrupt:
            print("\nGemma: Interrupted. Goodbye Sir.")
            break

if __name__ == "__main__":
    chat_with_gemma()
