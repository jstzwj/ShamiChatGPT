
def none_or(obj, or_obj):
    if obj is None:
        return None
    else:
        return or_obj

class Author(object):
    def __init__(self) -> None:
        self.role = None
        self.name = None
        self.metadata = None
    
    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        out = Author()
        out.role = data["role"]
        out.name = data["name"]
        out.metadata = data["metadata"]
        return out

    def to_dict(self):
        return {
            "role": self.role,
            "name": self.name,
            "metadata": self.metadata,
        }

class Content(object):
    def __init__(self) -> None:
        self.content_type = None
        self.parts = None
    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        out = Content()
        out.content_type = data["content_type"]
        out.parts = data["parts"]
        return out

    def to_dict(self):
        return {
            "content_type": self.content_type,
            "parts": self.parts,
        }

class Message(object):
    def __init__(self) -> None:
        self.id = None
        self.author = None
        self.create_time = None
        self.update_time = None
        self.content = None
        self.end_turn = None
        self.weight = None
        self.metadata = None
        self.recipient = None
    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        out = Message()
        out.id = data["id"]
        out.author = Author.from_dict(data["author"])
        out.create_time = data["create_time"]
        out.update_time = data["update_time"]
        out.content = Content.from_dict(data["content"])
        out.end_turn = data["end_turn"]
        out.weight = data["weight"]
        out.metadata = data["metadata"]
        out.recipient = data["recipient"]
        return out

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author.to_dict(),
            "create_time": self.create_time,
            "update_time": self.update_time,
            "content": self.content.to_dict(),
            "end_turn": self.end_turn,
            "weight": self.weight,
            "metadata": self.metadata,
            "recipient": self.recipient,
        }

class ChatMessage(object):
    def __init__(self) -> None:
        self.id = None
        self.message = None
        self.parent = None
        self.children = None
    
    @classmethod
    def from_dict(cls, data):
        if data is None:
            return None
        out = ChatMessage()
        out.id = data["id"]
        out.message = Message.from_dict(data["message"])
        out.parent = data["parent"]
        out.children = data["children"]
        return out

    def to_dict(self):
        return {
            "id": self.id,
            "message": None if self.message is None else self.message.to_dict(),
            "parent": self.parent,
            "children": self.children,
        }


class History(object):
    def __init__(self) -> None:
        self.title = None
        self.create_time = None
        self.moderation_results = []
        self.current_node = None

        self.mapping = {}
    
    @classmethod
    def from_dict(cls, data):
        out = History()
        out.title = data["title"]
        out.create_time = data["create_time"]
        out.moderation_results = data["moderation_results"]
        out.current_node = data["current_node"]
        
        for index, msg in data["mapping"].items():
            out.mapping[index] = ChatMessage.from_dict(msg)

        return out

    def to_dict(self):
        return {
            "title": self.title,
            "create_time": self.create_time,
            "moderation_results": self.moderation_results,
            "current_node": self.current_node,
            "mapping": {k:v.to_dict() for k, v in self.mapping.items()},
        }

class Conversation(object):
    def __init__(self, session: 'ChatSession', id: str, title: str, create_time):
        self.session = session
        self.id = id
        self.title = title
        self.create_time = create_time
        self.history = None
    
    def __repr__(self) -> str:
        return f"{self.id} - {self.title} - {self.create_time}"
    
