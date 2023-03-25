import os
import io
import sys
import pyaudio
import wave
import speech_recognition as sr
import openai
from gtts import gTTS


r = sr.Recognizer()
openai.api_key = os.getenv('API_KEY')
completion = openai.ChatCompletion()


def speech_to_text(filename):
    with sr.AudioFile(filename) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)

        return text


def askgpt(question, chat_log=None):
    if chat_log is None:
        chat_log = [{'role': 'user', 'content': question}]
        response = completion.create(model='gpt-3.5-turbo', messages=chat_log)
        answer = response.choices[0]['message']['content']
        chat_log = chat_log + [{'role': 'assistant', 'content': answer}]
        return answer, chat_log


def text_to_speech(tts):
    language = 'en'
    myobj = gTTS(text=tts[0], lang=language, slow=False)
    myobj.save("output.mp3")
    os.system("mpg321 output.mp3")


def record_wav():
    chunk = 1024  
    sample_format = pyaudio.paInt16 
    channels = 1
    fs = 44100  
    seconds = 5

    p = pyaudio.PyAudio()  

    print('Recording...')

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = [] 

    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    p.terminate()

    print('Finished recording.')

    wf = wave.open("input.wav", "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    return


def main():
    record_wav()
    question = speech_to_text("input.wav")
    print(f"Question: {question}")
    response = askgpt(question)
    print(f"Response: {response}")
    text_to_speech(response)


if __name__ == "__main__":
    main()
    #record_wav()
