import openai
import tiktoken
import logging
import enum
from transformers import AutoTokenizer

class ChatGPTCalls:

    class ModelName(enum.Enum):
        GPT_4 = 'gpt-4'
        GPT_4_0314 = 'gpt-4-0314'
        GPT_4_32K = 'gpt-4-32k'
        GPT_4_32K_0314 = 'gpt-4-32k-0314'
        GPT_3_5_TURBO = 'gpt-3.5-turbo'
        GPT_3_5_TURBO_0301 = 'gpt-3.5-turbo-0301'
        TEXT_DAVINCI_003 = 'text-davinci-003'
        TEXT_DAVINCI_002 = 'text-davinci-002'
        CODE_DAVINCI_002 = 'code-davinci-002'
        CODE_CUSHMAN_001 = 'code-cushman-001'
        TEXT_CURIE_001 = 'text-curie-001'
        TEXT_BABBAGE_001 = 'text-babbage-001'
        TEXT_ADA_001 = 'text-ada-001'
        DAVINCI = 'davinci'
        CURIE = 'curie'
        BABBAGE = 'babbage'
        ADA = 'ada'

    MAX_ALLOWED_TOKENS = model_max_tokens = {
        ModelName.GPT_4: 8192,
        ModelName.GPT_4_0314: 8192,
        ModelName.GPT_4_32K: 32768,
        ModelName.GPT_4_32K_0314: 32768,
        ModelName.GPT_3_5_TURBO: 4096,
        ModelName.GPT_3_5_TURBO_0301: 4096,
        ModelName.TEXT_DAVINCI_003: 4097,
        ModelName.TEXT_DAVINCI_002: 4097,
        ModelName.CODE_DAVINCI_002: 8001,
        ModelName.CODE_CUSHMAN_001: 2048,
        ModelName.TEXT_CURIE_001: 2049,
        ModelName.TEXT_BABBAGE_001: 2049,
        ModelName.TEXT_ADA_001: 2049,
        ModelName.DAVINCI: 2049,
        ModelName.CURIE: 2049,
        ModelName.BABBAGE: 2049,
        ModelName.ADA: 2049,
    }



    def __init__(self, api_key):
        openai.api_key = api_key
        self.models = openai.Model.list()
        openai.api_base = 'https://api.openai.com/v1'
        a = 4


    def send_request(self, prompt, max_tokens=None, n=1, temperature=0.5, top_p=1, model=ModelName.TEXT_DAVINCI_003):
        try:
            max_tokens = self._get_max_allowed_tokens(prompt, max_tokens, model)

            response = openai.Completion.create(
                model=model.value,
                # prompt=prompt,
                messages=[{'role': 'user', 'content': f'{prompt}'}],
                max_tokens=max_tokens,
                n=n,
                temperature=temperature,
                top_p=top_p
            )

            return response.choices[0].text.strip()

        except Exception as e:
            logging.error(f"Error while sending request to ChatGPT: {e}")
            raise e
        
    def send_chat_request(self, prompt, max_tokens=None, n=1, temperature=0.5, top_p=1, model=ModelName.GPT_3_5_TURBO_0301):
        try:
            max_tokens = self._get_max_allowed_tokens(prompt, max_tokens, model)

            response = openai.ChatCompletion.create(
                model=model.value,
                messages=[
                    {
                        'role': 'user',
                        'content': f'{prompt}'
                    }
                ],
                # max_tokens=max_tokens,
                n=n,
                temperature=temperature,
                top_p=top_p,
            )

            return response.choices[0]['message']['content']

        except Exception as e:
            logging.error(f"Error while sending request to ChatGPT: {e}")
            raise e

    def _get_max_allowed_tokens(self, prompt, max_tokens, model):
        prompt_tokens = self._count_tokens(prompt)
        maximum_tokens_for_completition = ChatGPTCalls.MAX_ALLOWED_TOKENS[model] - prompt_tokens - 1
        if not max_tokens or max_tokens > maximum_tokens_for_completition:
            max_tokens = maximum_tokens_for_completition
        return max_tokens
    
    def _count_tokens(self, text) -> int:
        encoding = tiktoken.get_encoding("gpt2")
        num_tokens = len(encoding.encode(text))
        return num_tokens