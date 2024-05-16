from vrmAnalytics.logging import logger
from typing import List

class QueryParamsBuilder:
    def __init__(self, assignment_id: str, number_of_days: int, source: List[str], number_of_notes: int) -> None:
        self.assignment_id = assignment_id
        self.number_of_days = number_of_days
        self.source = source
        self.number_of_notes = number_of_notes

    def build_query_params(self):
        logger.info("Query building has started")

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

        logger.info(f"Query building is success, {query}, {params}")

        return query, params
