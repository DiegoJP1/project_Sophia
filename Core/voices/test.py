class Assistant:
    def __init__(self):
        self.name = "Sofía"

    def greet(self):
        return "Hola, ¿en qué puedo ayudarte?"

    def respond(self, message):
        if "hola" in message.lower() or "hey" in message.lower() or self.name.lower() in message.lower():
            return self.greet()
        else:
            return "Lo siento, no entendí eso."

# Función principal
def main():
    assistant = Assistant()

    # Bucle para escuchar y responder
    while True:
        user_input = input("Tú: ")
        response = assistant.respond(user_input)
        print(f"{assistant.name}: {response}")

        # Condiciones de salida del bucle
        if user_input.lower() == "adios":
            break

if __name__ == "__main__":
    main()
