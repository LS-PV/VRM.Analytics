import pyodbc
from openai import OpenAI
from flask import Flask, jsonify, request
import logging
from azure.identity import ManagedIdentityCredential
import struct



class AIResponse:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.assignment_id = ""
        self.number_of_days = 100000
        self.number_of_notes = 100000
        self.summary_line_count = 4
        self.source = ['Client', 'Internal', 'Agent', 'Auction', 'Remarketing', 'Debtor', 'Third-party', 'AutoIMS']
        self.flag = False

    def set_assignment(self, assignment_id, number_of_days=90, number_of_notes=0, summary_line_count=4, source=['Client', 'Internal', 'Agent', 'Auction', 'Remarketing', 'Debtor', 'Third-party', 'AutoIMS'], flag=False):
        self.assignment_id = assignment_id
        self.number_of_days = number_of_days
        self.number_of_notes = number_of_notes
        self.summary_line_count = summary_line_count
        self.source = source
        self.flag = flag

    def get_assignment_notes(self):
        try:
            server = 'vrm-synapse-workspace-prod-ondemand.sql.azuresynapse.net'
            database = 'vrm-prod-reporting'
            driver = '{ODBC Driver 17 for SQL Server}'

            # Test
            
            azure_credential = ManagedIdentityCredential(logging_enable=True,client_id="%client_id%",)
                        
            token_bytes = azure_credential.get_token('https://database.windows.net/.default').token.encode('utf-16-le')
            token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)
            
            connection_string = f"Driver={driver};Server={server};Database={database};"

            logging.info(connection_string)

            full_notes = []
            sources = []

            query = """
                SELECT Notes, Source
                FROM VRM_EX_Notes
                WHERE AssignmentId = ? 
                AND NoteCreatedDate > DATEADD(day, ?, CAST(GETDATE() AS DATE))
                AND Source IN ({})
                ORDER BY NoteCreatedDate DESC
                OFFSET 0 ROWS
                FETCH NEXT ? ROWS ONLY
            """.format(','.join(['?']*len(self.source)))

            params = [self.assignment_id, self.number_of_days * -1] + self.source + [self.number_of_notes]
            
            with pyodbc.connect(connection_string, attrs_before={1256: token_struct}).cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                for row in rows:
                    full_notes.append(row[0].replace('\n', ' ').replace('\r', ''))
                    sources.append(row[1])
            
            if (self.flag):
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

            return instructions
        
        except Exception as e:
            error_msg = f"Error retrieving assignment notes: {e}"
            logging.error(error_msg)
            return error_msg

    def generate_response(self):
        response = []
        try:
            for note in self.get_assignment_notes():
                instructions = "Below are a list of notes, delimited by  ---------.  The first note below is the latest note. Can you summarize them in {self.summary_line_count} bullet points, in chronological order. The first part of the summary paragraph should be the latest note. " + note
                chat_completion = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": instructions,
                        }
                    ],
                    model="gpt-3.5-turbo",
                )
                response.append(chat_completion.choices[0].message.content)

            return response
        
        except Exception as e:
            error_msg = f"Error generating response: {e}"
            logging.error(error_msg)
            return error_msg

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

chat_bot = AIResponse(api_key="%API_KEY%")

@app.route('/assignment', methods=['POST'])
def assignment():
    try:
        data = request.get_json()
        assignment_id = data.get('assignmentId')
        number_of_days = int(data.get('numberOfDays', 100000))
        number_of_notes = int(data.get('numberOfNotes', 100000))
        summary_line_count = int(data.get('summaryLineCount', 4))
        no_limit = bool(data.get('noLimit', False))
        src = data.get('source')
        flag = False

        print(src)

        if src == 'Client':
            src = ['Client']
        elif src == 'Internal':
            src = ['Internal']
        elif src == 'Agent':
            src = ['Agent']
        elif src == 'All':
            src = ['Client', 'Internal', 'Agent']
            flag = True
        else:
            src = ['Client', 'Internal', 'Agent', 'Auction', 'Remarketing', 'Debtor', 'Third-party', 'AutoIMS']

        if no_limit:
            number_of_days = 100000
            number_of_notes = 100000            

        if assignment_id:
            chat_bot.set_assignment(assignment_id, number_of_days, number_of_notes, summary_line_count, src, flag)
            response = chat_bot.generate_response()
            if len(response) == 1:
                return jsonify({
                    "Summary": {
                        "Source": {
                            "Source": src,
                            "Summary": response[0]
                        }
                    }
                })
            else:
                return jsonify({
                    "Summary": {
                        "Source": {
                            "Source": "Client",
                            "Summary": response[0]
                        },
                        "Source": {
                            "Source": "Internal",
                            "Summary": response[1]
                        },
                        "Source": {
                            "Source": "Agent",
                            "Summary": response[0]
                        },
                    }
                })

        else:
            return jsonify({"error": "AssignmentId is required in the request"}), 400
    except Exception as e:
        error_msg = f"Error processing request: {e}"
        logging.error(error_msg)
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True)