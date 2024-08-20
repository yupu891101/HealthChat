from bark.generation import generate_text_semantic, preload_models
from bark.api import semantic_to_waveform
from bark import SAMPLE_RATE
from opencc import OpenCC
import soundfile as sf
import numpy as np
import langid
import nltk
import re

class Bark():
    def __init__(self):
        preload_models()
        self.opencc = OpenCC('t2s')
        self.sentences = []
        self.stop_event = False
    
    def contains_traditional_chinese(self, text):
        traditional_characters_pattern = re.compile(
            r'[㐀-䶵⼀-⿕一-龥]'
        )
        return bool(traditional_characters_pattern.search(text))
    
    def remove_emoji(self, text):
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002700-\U000027BF"  # dingbats
            u"\U0000FE00-\U0000FE0F"  # Variation Selectors
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "]+", flags=re.UNICODE)
        return emoji_pattern.sub(r'', text)
    
    def split_chinese_sentences(self, text):
        sentences = re.split(r'(?<=[。！？])', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def detect_language(self, text):
        lang, _ = langid.classify(text)
        return lang

    def get_speaker(self, language, gender):
        speakers = {
            "male": {
                "en": "v2/en_speaker_4",
                "zh": "v2/zh_speaker_1",
                "de": "v2/de_speaker_6",
                "it": "v2/it_speaker_4",
                "ko": "v2/ko_speaker_1",
                "ja": "v2/ja_speaker_2",
            },
            "female": {
                "en": "v2/en_speaker_9",
                "zh": "v2/zh_speaker_9",
                "de": "v2/de_speaker_3",
                "it": "v2/it_speaker_9",
                "ko": "v2/ko_speaker_0",
                "ja": "v2/ja_speaker_3",
            }
        }
        return speakers[gender].get(language, "v2/en_speaker_9")

    def generate_audio(self, text, gender):
        if self.contains_traditional_chinese(text):
            text = self.opencc.convert(text)

        remove_emoji_text = self.remove_emoji(text)
        new_text = remove_emoji_text.replace("\n", " ").strip()
        
        if self.detect_language(new_text) == 'zh':
            self.sentences = self.split_chinese_sentences(new_text)
        else:
            self.sentences = nltk.sent_tokenize(new_text)

        GEN_TEMP = 1.0
        silence = np.zeros(int(0.25 * SAMPLE_RATE))

        print("\n------------------------------Start generating audio------------------------------\n")
        pieces = []
        for sentence in self.sentences:
            print(f"[Sentence] {sentence}")
            language = self.detect_language(sentence)
            print(f"[Language] {language}")
            speaker = self.get_speaker(language, gender)
            semantic_tokens = generate_text_semantic(
                sentence,
                history_prompt=speaker,
                temp=GEN_TEMP,
                min_eos_p=0.05,
            )

            audio_array = semantic_to_waveform(semantic_tokens, history_prompt=speaker,)
            pieces += [audio_array, silence.copy()]
        audio_output = np.concatenate(pieces)
        
        full_audio = np.concatenate(pieces)
        sf.write(f'change_voice/voice_example_{gender}.wav', full_audio, SAMPLE_RATE)
        
        return (SAMPLE_RATE, audio_output)
