from vrmAnalytics.logging import logger
from typing import Dict, List
from openai import OpenAI
import os

class ChatGPTConnection:
    def __init__(self) -> None:
        self.api_key: str = None
        self.CONFIG: Dict = None
        self.gpt: OpenAI = None

    def __get_details(self) -> None:
        self.CONFIG = {}
        self.CONFIG['GPT_API_KEY'] = os.getenv('OPENAI_API_KEY')

    def __get_connection(self) -> None:
        if self.CONFIG == None:
            self.__get_details()
        self.api_key = self.CONFIG['GPT_API_KEY']
        self.gpt = OpenAI(api_key=self.api_key)
        logger.info("CHATGPT is initiated")
    
    def fetch_summary(self, instructions: Dict[str, str], line_count: int) -> Dict[str, List[str]]:
        try:
            if self.gpt == None:
                self.__get_connection()

            prefix = f"""Below are a list of notes, delimited by ---------. The first note below is the latest note. Can you summarize them in {line_count} numbered points, in chronological order. The first part of the summary should be the latest note. Remove every special characters and ---------. The summary should be clean and structured, with each numbered point clearly separated by \n."""

            data = {}
            
            logger.info("Feeding Notes to CHATGPT")
            for source_key in instructions:
                instruction = prefix + instructions[source_key]
                summaries = self.gpt.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": instruction}
                    ]
                )
                data[source_key] = summaries.choices[0].message.content
            logger.info("Generated Summaries from CHATGPT")

            response = {}

            for key in data:
                response[key] = data[key].strip().split('\n')

            print(response)

            return response
        
        except Exception as e:
            error_msg = f"Error retrieving Summary from GPT: {e}"
            logger.error(error_msg)
            return error_msg
