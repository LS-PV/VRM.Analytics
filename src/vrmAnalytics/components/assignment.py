from vrmAnalytics.entity import AssignmentConfig
from vrmAnalytics.logging import logger
from typing import Dict

class AssignmentData:
    def __init__(self, data: Dict):
        self.data = data

    def validate_assignment_data(self) -> AssignmentConfig:
        assignment_id = self.data.get('assignmentId')
        number_of_days = int(self.data.get('numberOfDays', 100000))
        number_of_notes = int(self.data.get('numberOfNotes', 100000))
        summary_line_count = int(self.data.get('summaryLineCount', 4))
        no_limit = bool(self.data.get('noLimit', False))
        source = self.data.get('source')
        flag =  bool(self.data.get('flag', False))

        if not assignment_id:
            raise ValueError("Please provide an Assignment Id")
        if not source:
            raise AssertionError("Please provide a Source")
        
        if no_limit:
            number_of_days = 100000
            number_of_notes = 100000
        
        logger.info(f"Request data is validated")

        return AssignmentConfig(
            assignment_id=assignment_id,
            number_of_days=number_of_days,
            number_of_notes=number_of_notes,
            summary_line_count=summary_line_count,
            source=source,
            flag=flag,
            no_limit=no_limit
        )
