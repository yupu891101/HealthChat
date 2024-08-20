from transformers import pipeline

class TaiwanLlama:
    def __init__(self):
        self.chat = pipeline("text-generation", model="./taiwan_llama/module_v7", model_kwargs={"load_in_8bit": True}, device_map="auto")
        self.history = []
        self.instructions = {
            'role': 'system',
            'content': (
                "你是一位富有同情心和同理心的心理諮商師。你需要為面臨各種心理問題的使用者提供心理支持、指導和幫助。"
                "你應該仔細閱讀使用者的敘述，提供深思熟慮且不帶偏見的回應，並鼓勵用戶在必要時尋求專業協助。"
                "你的目標是透過回應使用者的對話來紓解他們的心理壓力。"
                "例如，當用戶說他們覺得沮喪時，你可以回應：「你最近遇到什麼困難了嗎？可以跟我說說你的感受。」" 
                "用中文回答使用者的對話。"
                "回答的時候簡潔有力，不要太長，絕對不要超過五句話。"
            )
        }
        self.history.append(self.instructions)

    def send_message(self, message):
        message_dict = {
            'role': 'user',
            'content': message
        }
        self.history.append(message_dict)
        print("\nStart generating chatbot text...")
        sys_response = self.chat(
            text_inputs=self.history
        )
        self.history.append({
            'role': 'assistant',
            'content': sys_response[0]['generated_text'][-1]['content']
        })
        return sys_response[0]['generated_text'][-1]['content']
    
if __name__ == "__main__":
    chatbot = TaiwanLlama()
    while True:
        message = input("You: ")
        response = chatbot.send_message(message)
        print(f"TaiwanLlama: {response}")