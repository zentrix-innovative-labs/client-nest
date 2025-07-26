from threads_api import ThreadsAPI

class ThreadsService:
    def __init__(self, username, password):
        self.api = ThreadsAPI()
        self.username = username
        self.password = password
        self.login()

    def login(self):
        self.api.login(self.username, self.password)

    def post(self, text):
        return self.api.post_thread(text) 