from tkinter import *
from tkinter import ttk
import threading
import bobok
import os

TEXT_COLOR = "white"
BACKGROUND_ONE = "#1D1D1D"
BACKGROUND_TWO = "#111111"
FONT = "Helvetica"
FONT_SIZE = 15
SAVE_CURSOR = 1
LAST_SAVE_FILE = "Default"

is_waiting_for_response = False

root = Tk()
root.geometry("1000x800+100+100")
root.config(background=BACKGROUND_ONE)
root.title("Bobok")

# Frame for chat and scrollbar
upper_frame = Frame(root, padx=10, pady=10)
upper_frame.config(background=BACKGROUND_TWO)
upper_frame.pack(fill=BOTH, expand=True)

# Scrollbar
scrollbar = Scrollbar(upper_frame)
scrollbar.config(background=BACKGROUND_ONE)
scrollbar.pack(side=RIGHT, fill=Y)

# Text box for chat
chat_text = Text(upper_frame, yscrollcommand=scrollbar.set, wrap=WORD)
chat_text.config(background=BACKGROUND_ONE, foreground=TEXT_COLOR, font=(FONT, FONT_SIZE))
chat_text.pack(fill="x", expand=True)
chat_text.bind("<Key>", lambda e: "break")

# Configure scrollbar
scrollbar.config(command=chat_text.yview)

# Entry box
prompt_input = Entry(upper_frame)
prompt_input.config(background=BACKGROUND_ONE, foreground=TEXT_COLOR, font=(FONT, FONT_SIZE))
prompt_input.pack(fill=X, padx=5, pady=5)

def read_input():
    
    user_text = prompt_input.get().strip()
    if user_text and not is_waiting_for_response: # only request if AI is ready and if input is not empty
        # Append user message
        chat_text.insert(END, f"You: {user_text}\n\n")
        chat_text.see(END)  # auto-scroll to bottom

        def get_bobok_answer():
            global is_waiting_for_response
            is_waiting_for_response = True
            # Get Bobok's answer
            answer = bobok.answer(user_text)

            # Append Bobok's reply
            chat_text.insert(END, f"Bobok: {answer}\n")
            chat_text.insert(END, "--"*20 + "\n")
            chat_text.see(END)
            is_waiting_for_response = False

            # Read Bobok's reply
            bobok.read(answer)


        # Clear entry
        prompt_input.delete(0, END)
        # Run Bobok in background thread
        threading.Thread(target=get_bobok_answer, daemon=True).start()

submit_prompt = Button(upper_frame, text="Submit", command=read_input)
submit_prompt.config(background=BACKGROUND_ONE, foreground=TEXT_COLOR)
submit_prompt.pack(pady=5)

lower_frame = Frame(root)
lower_frame.config(background=BACKGROUND_TWO)
# Column and row configuration (makes it align nicely)
lower_frame.columnconfigure(0, weight=1)
lower_frame.columnconfigure(1, weight=1)
lower_frame.rowconfigure(0, weight=1)
lower_frame.rowconfigure(1, weight=1)
lower_frame.rowconfigure(2, weight=1)
lower_frame.pack(fill=X, side=BOTTOM, padx=10, pady=10)

file_list = Listbox(lower_frame)
file_list.config(background=BACKGROUND_ONE, foreground=TEXT_COLOR, font=(FONT, FONT_SIZE))
file_list.grid(column=0, rowspan=3)

def fill_file_list():
    file_list.delete(0, END)
    try:
        files = os.listdir("./conversations/")
        for f in files:
            file_list.insert(END, f)
    except FileNotFoundError:
        os.makedirs("./conversations")
fill_file_list()

# Save and load input
file_input = Entry(lower_frame)
file_input.config(background=BACKGROUND_ONE, foreground=TEXT_COLOR, font=(FONT, FONT_SIZE))
file_input.grid(column=1, row=0)


def exit(from_load = False):
    global LAST_SAVE_FILE
    if not from_load:
        filename = file_input.get()
        LAST_SAVE_FILE = filename
        bobok.save(filename)
        chat_text.delete("1.0",END)
    else:
        bobok.save(LAST_SAVE_FILE)
        chat_text.delete("1.0",END)
    fill_file_list()


exit_button = Button(lower_frame, text="Exit and Save", command=exit)
exit_button.config(background=BACKGROUND_ONE, foreground=TEXT_COLOR)
exit_button.grid(column=1, row=1)

def load():
    exit(from_load=True) # exit so it does not insert over it 
    filename = file_input.get()
    history = bobok.load(filename)
    chat_text.insert("1.0", history)
    chat_text.insert(END, "--"*20 + "\n")

load_button = Button(lower_frame, text="Load", command=load)
load_button.config(background=BACKGROUND_ONE, foreground=TEXT_COLOR)
load_button.grid(column=1, row=2)

# Bind Enter key to send message
prompt_input.bind("<Return>", lambda event: read_input())

root.mainloop()
