class UserData:
    def __init__(
            self,
            user_id: int,
            username: str,
            full_name: str
    ):
        self.full_name = full_name
        self.username = username
        self.user_id = user_id
