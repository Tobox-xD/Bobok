import random
import requests
import pandas as pd
import datetime
from ollama import Client
import pyttsx4
import re
import variables

# Setting up the AI
llama_3_3 = Client(host=variables.URL, timeout=500)

# Setting up TTS
engine = pyttsx4.init()

# Function for reloading the voice
def load_voice(voice):
    global engine
    voices = engine.getProperty("voices")
    try:
        user_language_preference = int(voice)
    except:
        user_language_preference = 0 # default to language 2
    engine.setProperty('voice', voices[user_language_preference].id)  # safer than hardcoding registry path

# Setting up the Mensaplan
today = datetime.date.today()
calenderweek = today.isocalendar()[1]
mensa_plan = requests.get(f"https://www.stwno.de/infomax/daten-extern/csv/UNI-R/{calenderweek}.csv?t=1762161964")
with open(f"mensaplans/mensaplanKW{calenderweek}.csv", "w", encoding="utf-8") as file:
    file.write(mensa_plan.text.replace("\r",""))
table = pd.read_csv(
    f"mensaplans/mensaplanKW{calenderweek}.csv",
    encoding="utf-8",
    sep=";",
    on_bad_lines="skip"
)
# Only using the Student relevant columns for performance
table = table[["datum", "tag", "name", "stud"]].rename(
    columns={
        "stud": "price",
        "datum": "date",
        "tag": "day"
    }
)


settings_dict = {"tts": "True", "language" : "2"}
# loading Settings
def load_settings():
    global settings_dict
    try:
        with open("settings.txt", "r") as file:
            settings = file.readlines()
            settings_dict["tts"] = settings[0].strip()
            settings_dict["language"] = settings[1].strip()
    # if there is no file create one
    except:
        with open("settings.txt", "w") as file:
            file.writelines(["True\n", "0"])

def update_settings(tts_update, language_update):
    global settings_dict
    with open("settings.txt", "w") as file:
        file.writelines([f"tts_update\n", language_update])
        settings_dict["tts"] = tts_update
        settings_dict["language"] = language_update
    load_voice(language_update)

# Loading settings and voice
load_settings()
load_voice(settings_dict["language"])

# Providing the AI with context 
pre_context  = f"""
    YOUR NAME IS BOBOK.
    DO NOT REINTRUDUCE YOURSELF
    Now you are a cook at the Mensa at the University of Regensburg and you are employed to help students of the university to find the best fitting meal.
    You are also employed to chat to the students so they wont feel so lonely.
    You like to make food related puns from time to time.
    mensaplan: {table.to_string()}
    Today is: {today}
    KEEP YOUR ANSWERS AS SHORT AS ANYHOW POSSIBLE BUT DO NOT DROP TOO MANY DETAILS
"""

context = pre_context

# History for storing the conversation
history = ""

# Running the AI
def answer(prompt):
    global history, context
    # Append history for User input
    history += f"[{datetime.datetime.now()}] You: {prompt}\n"
    messages = [ { "role" : "user", "content" : context + " " + prompt}] # Give the context and the input to the model
    llm_analysis = llama_3_3.chat(model='llama3.3:70b', messages=messages) # Calculate response
    answer = llm_analysis['message']['content'] # Answer to Sting
    # Append history for answer
    history +=  f"[{datetime.datetime.now()}] Bobok: {answer}\n"
    # Append context
    context +=  " " + prompt + " " + answer # ugly but the AI can interpret it 
    return answer

def read(text):
    if settings_dict["tts"] == "True":
        # Read out answer
        engine.say(text)
        engine.runAndWait()
    else:
        return

def save(new_filename):
    global history,context
    filename = new_filename
    if filename == "":
        filename = random.randint(1,10000)
    # Save history to a file
    with open(f"./conversations/{filename}.txt", "a", encoding="utf-8") as savefile:
        savefile.write(history)

    # Clear all variables for AI Memory
    context = pre_context
    history = ""

def load(filename):
    global context
    # Loading history from a file
    with open(f"./conversations/{filename}.txt", "r", encoding="utf-8") as savefile:
        old_history = savefile.read()
    # initialize all variables for AI Memory
    old_history = re.sub(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+\] ', '', old_history)
    context += old_history
    return old_history