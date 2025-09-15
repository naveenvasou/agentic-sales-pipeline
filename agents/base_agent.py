from typing import Dict, Any
import time
import logging
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO)

class BaseAgent:
    def __init__(
        self,
        name: str,
        llm=None,
        prompt_template: str = "",
        tools: Dict[str, Any] = None,
        max_retries: int = 3
    ):
        self.name = name
        self.llm = llm
        self.prompt = PromptTemplate(input_variables=["state"], template=prompt_template)
        self.tools = tools or {}
        self.max_retries = max_retries
        
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        
        attempt = 0
        while attempt < self.max_retries:
            try:
                logging.info(f"[{self.name}] Running agent. Attempt {attempt+1}")
                prompt_input = self.prompt.format(state=state)
                response = self.llm.predict(prompt_input)
                state = self.process_response()
                logging.info(f"[{self.name}] Completed Successfully")
                return state
            except Exception as e:
                logging.warning(f"[{self.name}] Error: {e}")
                attempt +=1
                time.sleep(1)
            logging.error(f"[{self.name}] Failed after {self.max_retries} attemps")
            state[f"{self.name}_status"] = "error"
            return state
        
    def process_response(self, response: str, state: Dict[str, Any]) -> Dict[str, Any]:
        
        raise NotImplementedError("Each agent must implemetn process_response method.")
    