import tkinter as tk
from googletrans import Translator
import threading
import speech_recognition as sr
import pywhatkit
from gtts import gTTS
import os
import openai

# Set your OpenAI API key
openai.api_key = "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"  


class SpeechInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Recognition and Interaction")
        self.root.geometry("600x500")

        self.target_language = "te"
        self.create_widgets()

    def create_widgets(self):
        self.root.tk_setPalette(background="#f0f0f0", foreground="#333")

        frame = tk.Frame(self.root, bg="#ffffff", padx=20, pady=20)
        frame.pack(pady=20)

        label_font = ("Helvetica", 14, "bold")

        tk.Label(frame, text="Spoken Input:", font=label_font, bg="#ffffff").pack(
            pady=10
        )

        input_text_font = ("Times 20 italic bold", 12, "bold")
        self.input_text = tk.Text(
            frame, wrap=tk.WORD, width=50, height=2, font=input_text_font
        )
        self.input_text.pack(pady=10)

        tk.Button(
            frame,
            text="Start Speaking",
            command=self.start_listening,
            bg="#55186f",
            fg="white",
            font=label_font,
        ).pack(pady=10)

        tk.Label(frame, text="Textual Output:", font=label_font, bg="#ffffff").pack(
            pady=10
        )

        output_text_font = ("Comic Sans MS", 12, "bold")
        self.output_text = tk.Text(
            frame, wrap=tk.WORD, width=50, height=10, font=output_text_font
        )
        self.output_text.pack(pady=10)

    def start_listening(self):
        threading.Thread(target=self.listen_and_process).start()

    def listen_and_process(self):
        spoken_text = recognize_speech()
        if spoken_text:
            print(f"YOU SAID: {spoken_text}")
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, spoken_text)

            if "alexa" in spoken_text.lower():
                spoken_text = spoken_text.lower().replace("alexa", "")
                info = self.interact_with_chatgpt(spoken_text)
                self.display_output(info)
            elif "play" in spoken_text:
                spoken_text = spoken_text.replace("play", "")
                pywhatkit.playonyt(spoken_text)
                self.display_output(f"Playing {spoken_text} on YouTube.")
            else:
                translated_text = translate_text(spoken_text, self.target_language)
                self.display_output(translated_text)

    def interact_with_chatgpt(self, query):
        try:
            # Make a request to ChatGPT using the OpenAI API
            response = openai.Completion.create(
                engine="text-davinci-002",
                prompt=f"Extract information about {query}",
                max_tokens=150,
            )
            info = response.choices[0].text.strip()
            return info
        except Exception as e:
            print(f"Error interacting with ChatGPT: {e}")
            return "Error interacting with ChatGPT."

    def display_output(self, output_text):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output_text)
        talk(output_text)


def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Please speak something...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=5)
        try:
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results: {e}")
            return None


def translate_text(text, target_language):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text


def talk(text, use_voice=True):
    if use_voice:
        tts = gTTS(text=text, lang="en")
        tts.save("output.mp3")
        os.system("start output.mp3")


if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechInterface(root)
    root.mainloop()
