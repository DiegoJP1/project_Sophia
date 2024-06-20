import pyttsx3

def say_text(text, voice_name=None):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')

    if voice_name:
        selected_voice = None
        for voice in voices:
            if voice.name.lower() == voice_name.lower():
                selected_voice = voice
                break

        if selected_voice:
            engine.setProperty('voice', selected_voice.id)
        else:
            print(f"Voz '{voice_name}' no encontrada. Usando la voz por defecto.")

    engine.say(text)
    engine.runAndWait()

if __name__ == "__main__":
    text = "Hola, estoy utilizando la síntesis de voz en Python con pyttsx3."
    voice_name = "sabina"  
    say_text(text, voice_name)
