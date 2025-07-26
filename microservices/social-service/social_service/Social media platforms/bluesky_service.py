from atproto import Client, models

class BlueskyService:
    def __init__(self, identifier, password):
        self.client = Client()
        self.identifier = identifier
        self.password = password
        self.login()

    def login(self):
        self.client.login(self.identifier, self.password)

    def post(self, text):
        post = models.ComAtprotoRepoCreateRecord.Data(
            repo=self.client.me.did,
            collection='app.bsky.feed.post',
            record={
                'text': text,
                'createdAt': models.get_iso_timestamp(),
            },
        )
        return self.client.com.atproto.repo.create_record(post)

    def get_profile(self):
        return self.client.com.atproto.identity.resolve_handle({'handle': self.identifier}) 