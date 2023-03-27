import azure.cognitiveservices.speech as speechsdk
import pyaudio
import wave
import os
import sys
import openai
import json

# Step 1: Set up the OpenAI API
openai.api_key = ""
api_endpoint = "https://api.openai.com/v1/engines/chatgpt"

def record_audio(output_filename):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(output_filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def transcribe_audio(subscription_key, region, audio_filename):
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    audio_input = speechsdk.audio.AudioConfig(filename=audio_filename)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    print("Transcribing...")

    result = speech_recognizer.recognize_once_async().get()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return("{}".format(result.text))
    else:
        return("No speech could be recognized: {}".format(result.no_match_details))

# Step 2: Call the ChatGPT API to send dataset information and transformations
def chatgpt_request(prompt):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

def main():
    if len(sys.argv) != 4:
        print("Usage: python send_audio_to_azure.py <subscription_key> <region> <output_wav_file>")
        sys.exit(1)

    subscription_key = sys.argv[1]
    region = sys.argv[2]
    output_wav_file = sys.argv[3]

    record_audio(output_wav_file)
    prompt = transcribe_audio(subscription_key, region, output_wav_file)
    response = chatgpt_request(prompt)
    print(f"ChatGPT response: {response}")

if __name__ == "__main__":
    main()