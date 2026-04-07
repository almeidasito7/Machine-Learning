from app.schemas.requests import AnalyzeRequest
from app.schemas.responses import AnalyzeResponse

def test_request_schema():
    data = AnalyzeRequest()
    assert data is not None


def test_response_schema():
    data = AnalyzeResponse(structures=[], total_structures=0)
    assert data.total_structures == 0