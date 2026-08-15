from db.database import Database
from dto.transactions import TransactionFilterDTO


class DatabaseController:
    def __init__(self):
        self.db = Database()

    def drop_tables(self):
        self.db.drop_tables()

    def create_tables(self):
        self.db.create_tables()

    def init_seed(self):
        self.db.set_balance(0.0)
        self.db.set_liquid(0.0)

    def reset(self):
        self.drop_tables()
        self.create_tables()
        self.init_seed()


class UserDataController:
    @staticmethod
    def controller_set_userdata(name, gender):
        if not name:
            name = ""
        db = Database()
        db.set_userdata(name, gender)

    @staticmethod
    def controller_fetch_userdata():
        db = Database()
        user_data = db.fetch_userdata()  # return a tuple

        return user_data


class SearchController:
    def __init__(self):
        pass

    def controller_search_transactions(query):
        db = Database()
        filter = TransactionFilterDTO()
        transactions = db.fetch_transactions(filter)

        query_lower = query.lower()
        filtered_transactions = [
            t for t in transactions
            if query_lower == t.name .lower() or query_lower == str(t.category)
        ]
        return filtered_transactions


if __name__ == "__main__":
    pass
