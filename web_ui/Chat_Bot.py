from taiwan_llama.taiwan_llama import TaiwanLlama
from web_ui.ollama_chat import Ollama_Chat
from web_ui.Bark import Bark
from web_ui.Tab1 import Tab1
import gradio as gr
import numpy as np
import subprocess
import whisper
import wave

class ChatBot():
    def __init__(self, mode='text', tab1: Tab1 = None) -> None:
        self.model = whisper.load_model('base', device = 'cuda')
        self.ollama = TaiwanLlama()
        self.bark = Bark()
        self.tab1 = tab1
        self.mode = mode
        self.history = []
    
    def print_like_dislike(self, x: gr.LikeData):
        print(x.index, x.value, x.liked)

    def add_message(self, message):
        self.mode = 'text'
        for x in message["files"]:
            self.history.append(((x,), None))
        if message["text"] is not None:
            self.history.append((message["text"], None))
        return self.history, gr.MultimodalTextbox(value=None, interactive=False)
    
    def transcribe(self, audio: np.ndarray):
        print("\nStarting transcription...")
        self.mode = 'audio'
        audio = audio[1].astype(np.float32) / 32768.0
        self.text = self.model.transcribe(audio)['text']
        self.history.append((self.text, None))
        return self.history

    def bot_response(self, messages, input_pt=None, keychange=None, speedup=None, gender='male'):
        if self.mode == 'text':
            last_user_msg = messages[-1][0] if messages else ""
            # bot_reply = self.ollama.send_message(last_user_msg, model=model)
            bot_reply = self.ollama.send_message(last_user_msg)
        else:
            # bot_reply = self.ollama.send_message(self.text, model=model)
            bot_reply = self.ollama.send_message(self.text)
        self.history.append((None, bot_reply))

        print("\n------------------------------Chat history------------------------------\n")
        i = 0
        for u, a in self.history:
            if i % 2 == 0:
                print(f"[User] {u}")
            else:
                print(f"[Assistant] {a}")
            i += 1
        
        sample_rate, np_array = self.bark.generate_audio(bot_reply, gender)
        array_int16 = np.array(np_array * 32767, dtype=np.int16)
        if not self.tab1.cloned:    
            return self.history, (sample_rate, array_int16)
        else:
            np_array = (np_array/np_array.max())*0.65*32768
            np_array = (np_array).astype(np.int16).tobytes()
            with wave.open('./DDSP-SVC/temp_audio.wav', 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(np_array)
            command = f"python main_diff.py -i ./temp_audio.wav -diff {input_pt} -o ./out_audio.wav -k {keychange} -speedup {speedup} -method 'dpm-solver' -kstep 100"
            process = subprocess.run(command, shell=True, text=True, capture_output=True, cwd=r"./DDSP-SVC")
            return self.history, './DDSP-SVC/out_audio.wav'

    def action(self, btn, audio_box):
        """Changes button text on click"""
        print(f"\nButton clicked. Current state: {btn}")
        if btn == '🔴  Speak':
            return '⏹️  Stop', None
        else:
            return '🔴  Speak', audio_box if audio_box is not None else None

    def check_btn(self, btn):
        """Checks for correct button text before invoking transcribe()"""
        if btn != '⏹️  Stop':
            # raise Exception('Recording...')
            pass

    @staticmethod
    def click_js():
        return """
        function audioRecord() {
            var xPathRes = document.evaluate('//*[contains(@class, "record-button")]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null); 
            if (xPathRes.singleNodeValue) {
                console.log("Record button found and clicked.");
                xPathRes.singleNodeValue.click();
            } else {
                console.error("Record button not found.");
            }
        }
        """
    
    def clear_history(self):
        self.history = []
        self.bark.stop_event = True
        self.tab1.cloned = False
        return [], gr.MultimodalTextbox(value=None, interactive=True), gr.Audio(value=None)
