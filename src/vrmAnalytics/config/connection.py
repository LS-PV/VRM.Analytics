from vrmAnalytics.logging import logger
import pyodbc
from pyodbc import Connection
from typing import Dict, List
import os

class ConnectionManager:
    def __init__(self) -> None:
        self.__connection: Connection = None
        self.CONFIG: Dict = None

    def __get_details(self) -> None:
        self.CONFIG = {}
        self.CONFIG['DB'] = os.getenv('DATABASE')
        self.CONFIG['USER'] = os.getenv('USER_NAME')
        self.CONFIG['PASSWORD'] = os.getenv('PASSWORD')
        self.CONFIG['SERVER'] = os.getenv('DEV_SERVER')
        self.CONFIG['DRIVER'] = os.getenv('DRIVER')
    
    def __getConnection(self) -> None:
        if self.CONFIG == None:
            self.__get_details()

        self.DB = self.CONFIG['DB']
        self.USER = self.CONFIG['USER']
        self.PASSWORD = self.CONFIG['PASSWORD']
        self.SERVER = self.CONFIG['SERVER']
        self.DRIVER = self.CONFIG['DRIVER']
        
        connection_string = f'DRIVER={self.DRIVER};SERVER={self.SERVER};DATABASE={self.DB};UID={self.USER};PWD={self.PASSWORD}'

        self.__connection = pyodbc.connect(connection_string)
        logger.info("Connection is initiated")

    def __removeConnection(self) -> None:
        self.__connection = None
        self.CONFIG = None
        logger.info("Connection ended successfully")

    def fetch_instructions(self, query, params, flag, source: List[str]) -> Dict[str, str]:
        try:
            if self.__connection == None:
                self.__getConnection()

            full_notes = []
            sources = []

            with self.__connection.cursor() as cursor:
                logger.info("Query execution started")
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    full_notes.append(row[0].replace('\n', ' ').replace('\t', ' ').replace('\r', ''))
                    sources.append(row[1])
                logger.info("Query execution complete")

            if flag:
                data = {'Client': [], 'Internal': [], 'Agent': []}
                for i in range(len(full_notes)):
                    if sources[i] == 'Client':
                        data['Client'].append(full_notes[i])
                    elif sources[i] == 'Internal':
                        data['Internal'].append(full_notes[i])
                    else:
                        data['Agent'].append(full_notes[i])
            else:
                data = {source[0]: []}
                for i in range(len(full_notes)):
                    data[source[0]].append(full_notes[i])

            instructions = {}
            for key in data:
                instructions[key] = '---------'.join(data[key])

            self.__removeConnection()
            return instructions
        
        except Exception as e:
            error_msg = f"Error retrieving Assignment Notes: {e}"
            logger.error(error_msg)
            return error_msg
