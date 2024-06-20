import whisper
import pyttsx3
from llama_cpp import Llama


class LlamaChat():
    def __init__(self):
        self.messages = []
        self.model = Llama(model_path='src/model/model-q8_0.gguf', n_ctx=1024)
        self.system_prompt = 'Ты - РуБот, русскоязычный автоматический ассистент. ' \
                             'Ты разговариваешь с людьми и помогаешь им практиковать русский язык.'

    def reset_msg(self):
        self.messages = []

    def add_msg(self, msg):
        self.messages.append({'role': 'user', 'content': msg})
        if len(self.messages) > 5:
            self.messages = self.messages[-5:]

    def get_llama_answer(self):
        messages_with_system_prompt = [
            {
                'role': 'system',
                'content': self.system_prompt
            }
        ]
        for message in self.messages:
            messages_with_system_prompt.append(message)

        response = self.model.create_chat_completion(messages=messages_with_system_prompt)
        print(response["choices"][0]["message"]["content"])
        return response["choices"][0]["message"]["content"]


class STT():
    def __init__(self):
        self.model = whisper.load_model("base")

    def run(self, audios):
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(audios)
        audio = whisper.pad_or_trim(audio)
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        # detect the spoken language
        _, probs = self.model.detect_language(mel)
        lang = max(probs, key=probs.get)
        print(f"Detected language: {max(probs, key=probs.get)}")
        # decode the audio
        result = self.model.transcribe(audios, fp16=False, language=lang)
        print(result)
        return " ".join([elem["text"] for elem in result['segments']])


class TTS():
    def __init__(self):
        self.model = pyttsx3.init()

    def run(self, text, filepath):
        self.model.save_to_file(text, filepath)
        self.model.runAndWait()
