from locust import HttpUser, task, between

class BenchmarkUser(HttpUser):
    # wait_time = between(1, 2)

    @task
    def cotacao(self):
        self.client.post("/cotacao", json={"empresa": "ABC", "valor": 100})
