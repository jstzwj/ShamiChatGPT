

class Conversation(object):
    def __init__(self, session: 'ChatSession', id: str, title: str, create_time):
        self.session = session
        self.id = id
        self.title = title
        self.create_time = create_time
    
    def __repr__(self) -> str:
        return f"{self.id} - {self.title} - {self.create_time}"