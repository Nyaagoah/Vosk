import pyaudio
import wave
import json
import pyttsx3
from vosk import Model, KaldiRecognizer
from padatious import IntentContainer

# Define the path to the Vosk model
model_path = "C:/Users/npuoc/Downloads/vosk-model-small-en-us-0.15/vosk-model-small-en-us-0.15"

# Initialize the Vosk model
model = Model(model_path)
rec = KaldiRecognizer(model, 16000)
rec.SetWords(True)

# Initialize the PyAudio
p = pyaudio.PyAudio()

# Define the audio stream
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=4000)
stream.start_stream()

# Initialize the TTS engine
engine = pyttsx3.init()

# Initialize Padatious IntentContainer
container = IntentContainer('intent_cache')

# Load intents and entities
container.load_file('intents/greeting.intent')
container.load_file('intents/stop.intent')
container.load_file('intents/container.intent')
container.load_file('entities/item.entity')
container.load_file('entities/place.entity')
container.train()

print("Listening...")

try:
    while True:
        data = stream.read(4000)
        if rec.AcceptWaveform(data):
            result = rec.Result()
            print(result)
            # Process the result and generate a response
            response = json.loads(result).get("text", "")
            if response:
                print(f"You said: {response}")
                # Recognize the intent
                intent = container.calc_intent(response)
                print(f"Intent: {intent.name}, Confidence: {intent.conf}")

                if intent.name == 'greeting':
                    reply = "Hello! How are you?"
                elif intent.name == 'stop':
                    reply = "Stopping..."
                    print(reply)
                    engine.say(reply)
                    engine.runAndWait()
                    break  # Exit the while loop and stop the script
                elif intent.name == 'container':
                    item = intent.matches.get('item', 'items')
                    place = intent.matches.get('place', 'somewhere')
                    reply = f"You keep your {item} in {place}."
                else:
                    reply = "I didn't catch that."

                print(reply)
                engine.say(reply)
                engine.runAndWait()
except KeyboardInterrupt:
    print("Keyboard interrupt detected.")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()


