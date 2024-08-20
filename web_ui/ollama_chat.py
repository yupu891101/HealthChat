import ollama

def colored(text: str, txt_color: str="white", bg_color: str='default', bright: bool=True):
    txt_dict = {
        'black':30, 'red':31, 'green':32, 'yellow':33,
        'blue':34, 'purple':35, 'cyan':36, 'white':37,
    }
    bg_dict = {
        'black':40, 'red':41, 'green':42, 'yellow':43,
        'blue':44, 'purple':45, 'cyan':46, 'white':47,
        'default':0,
    }
    if bright:
        return f"\033[{bg_dict[bg_color]};{txt_dict[txt_color]}m\033[1m{text}\033[0m"
    return f"\033[{bg_dict[bg_color]};{txt_dict[txt_color]}m{text}\033[0m"

class Ollama_Chat():
    def __init__(self) -> None:
        self.history = []
        self.instructions = {
            'role': 'system',
            'content': ""
        }
        self.ins_dict = {
            "llama3": (
                "You are a compassionate and empathetic AI therapist. Your role is to provide psychological support, "
                "guidance, and resources to users who may be dealing with a variety of mental health issues such as "
                "anxiety, depression, stress, relationship problems, and more. You should listen carefully, offer thoughtful "
                "and non-judgmental responses, and encourage users to seek professional help if necessary. Your goal is to "
                "create a safe and supportive environment for users to express their feelings and concerns."
            ),
            "module_v7": (
                "你是一位富有同情心和同理心的心理諮商師。你需要為面臨各種心理問題的使用者提供心理支持、指導和幫助。"
                "你應該仔細閱讀使用者的敘述，提供深思熟慮且不帶偏見的回應，並鼓勵用戶在必要時尋求專業協助。"
                "你的目標是透過回應使用者的對話來紓解他們的心理壓力。"
                "例如，當用戶說他們覺得沮喪時，你可以回應：「你最近遇到什麼困難了嗎？可以跟我說說你的感受。」" 
                "用中文回答使用者的對話。"
                "回答的時候盡量不要超過三句話。"
            )
        }
        self.history.append(self.instructions)

    def send_message(self, message, model='llama3'): # model='module_v7'
        print(colored(f"Model: {model}", 'green',bright=True))
        self.history[0]["content"] = self.ins_dict[model]
        message_dict = {
            'role': 'user',
            'content': message
        }
        self.history.append(message_dict)
        sys_response = ollama.chat(
            model=model,
            messages=self.history
        )
        self.history.append({
            'role': 'assistant',
            'content': sys_response['message']['content']
        })
        return sys_response['message']['content']

if __name__ == "__main__":
    chatbot = Ollama_Chat()
    while True:
        message = input("You: ")
        response = chatbot.send_message(message)
        print(f"Ollama: {response}")
