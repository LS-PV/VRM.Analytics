from flask import Flask, jsonify, request
from flask_cors import CORS
from vrmAnalytics.logging import logger
from vrmAnalytics.constants.query_params import QueryParamsBuilder
from vrmAnalytics.config.connection import ConnectionManager
from vrmAnalytics.config.chat_gpt import ChatGPTConnection
from vrmAnalytics.components.assignment import AssignmentData

app = Flask(__name__)
CORS(app=app)
app.logger.handlers = logger.handlers
app.logger.setLevel(logger.level)

@app.route('/assignment', methods=['POST'])
def assignment():
    try:
        data = request.get_json()
        logger.info(f"Request data: {data}")

        validated_assignment_data = AssignmentData(data).validate_assignment_data()

        assignment_id = validated_assignment_data.assignment_id
        number_of_days = validated_assignment_data.number_of_days
        number_of_notes = validated_assignment_data.number_of_notes
        summary_line_count = validated_assignment_data.summary_line_count
        source = validated_assignment_data.source
        flag = validated_assignment_data.flag

        query, params = QueryParamsBuilder(assignment_id=assignment_id, number_of_days=number_of_days, number_of_notes=number_of_notes, source=source).build_query_params()

        connection = ConnectionManager()
        instructions = connection.fetch_instructions(query=query, params=params, flag=flag)

        chat_bot = ChatGPTConnection()
        response = chat_bot.fetch_summary(notes_source_data=instructions, line_count=summary_line_count)
        
        logger.info("Sending response to user successfully")
        return jsonify({"data": response}), 200

    except (ValueError, AssertionError) as e:
        return jsonify({"error": e}), 400
    
    except Exception as e:
        error_msg = f"Error processing the request: {e}"
        logger.error(error_msg)
        return jsonify({"error": error_msg}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
