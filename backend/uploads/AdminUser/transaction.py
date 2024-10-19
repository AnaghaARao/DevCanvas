# transaction.py

from auth import AuthService

class Transaction:
    def __init__(self):
        self.auth_service = AuthService()

    def perform_transaction(self, username):
        self.auth_service.authenticate(username)
        print(f"Transaction performed for {username}.")
        self.auth_service.logout()
