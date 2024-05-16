from vrmAnalytics.logging import logger
from typing import Dict
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
        logger.info("GPT API is initiated")
        self.api_key = self.CONFIG['GPT_API_KEY']
        self.gpt = OpenAI(api_key=self.api_key)
    
    def fetch_summary(self, notes_source_data, line_count):
        try:
            if self.gpt == None:
                self.__get_connection()

            prefix = f"Below are a list of notes, delimited by  ---------.  The first note below is the latest note. Can you summarize them in {line_count} bullet points, in chronological order. The first part of the summary paragraph should be the latest note."

            response = []
            
            logger.info("Requesting GPT Summaries")
            for note in notes_source_data:
                instructions = prefix + note
                chat_response = self.gpt.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": instructions}
                    ]
                )

                response.append(chat_response.choices[0].message.content)

            logger.info("Received Summaries from GPT")
            return response
        
        except Exception as e:
            error_msg = f"Error retrieving Summary from GPT: {e}"
            logger.error(error_msg)
            return error_msg
