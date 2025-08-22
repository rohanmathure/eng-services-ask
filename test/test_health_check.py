class TestHealthCheck:
    def test_health_check(self, test_app):
        response = test_app.get("/health")
        assert response.status_code == 200