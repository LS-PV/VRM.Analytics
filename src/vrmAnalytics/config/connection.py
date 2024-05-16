from vrmAnalytics.logging import logger
import pyodbc
from pyodbc import Connection
from typing import Dict
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

    def __removeConnection(self) -> None:
        self.__connection = None
        self.CONFIG = None

    def fetch_instructions(self, query, params, flag):
        try:
            if self.__connection == None:
                logger.info("Connection is initiated")
                self.__getConnection()

            full_notes = []
            sources = []

            logger.info("Query execution started")
            with self.__connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    full_notes.append(row[0].replace('\n', ' ').replace('\r', ''))
                    sources.append(row[1])
            logger.info("Query is executed successfully")

            if flag:
                instructions = [[], [], []]
                for i in range(len(full_notes)):
                    if (sources[i] == 'Client'):
                        instructions[0].append(full_notes[i])
                    elif (sources[i] == 'Internal'):
                        instructions[1].append(full_notes[i])
                    else:
                        instructions[2].append(full_notes[i])
                
                instructions = ['---------'.join(i) for i in instructions]
            else:
                instructions = ['---------'.join(full_notes)]

            self.__removeConnection()
            logger.info("Connection is ended successfully")

            return instructions
        
        except Exception as e:
            error_msg = f"Error retrieving Assignment Notes: {e}"
            logger.error(error_msg)
            return error_msg
