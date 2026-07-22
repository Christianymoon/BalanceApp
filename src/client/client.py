from flet import Page
import logging

class ClientStorage:
    def __init__(self, page: Page):
        self.page = page 
        self.prefix = "christianymoon.finance."


    def create_key(self, key: str, value = any) -> None:
        try:
            self.page.client_storage.set(self.prefix + key, value)
            return True
        except:
            logging.error(f"Error al establecer el valor de llave {key} con valor {value}")
            return False 


    def get_value(self, key: str) -> any:
        """Returns none if value not found"""
        value = self.page.client_storage.get(self.prefix + key)
        return value 

    def set_value(self, key: str, value: any):
        try:
            self.remove_value(key)
            self.create_key(key, value)
            return True
        except: 
            logging.error("Error al eliminar y crear el valor de llave")
            return False

    def remove_value(self, key: str) -> None:
        self.page.client_storage.remove(self.prefix + key)

    def clear_values(self):
        self.page.client_storage.clear()