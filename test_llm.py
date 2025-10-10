from src.config import Config
from src.llm_client import LLMClient

def main():
    config = Config()
    llm = LLMClient(config.llm_base_url, config.llm_model, config.system_prompt)
    
    messages = [{"role": "user", "content": "Привет! Как дела?"}]
    response = llm.get_response(messages)
    print(f"Ответ: {response}")

if __name__ == '__main__':
    main()

