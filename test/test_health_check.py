import requests


class TestHealthCheck:
    def test_health_check(self):
        url = "http://localhost:8888/health"
        response = requests.get(url)
        assert response.status_code == 200