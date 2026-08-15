import logging

from db.database import Database


class CategoriesController():
    def __init__(self):
        pass

    def set_category(self, name, description=""):
        db = Database()
        try:
            id_ = db.set_category(name, description)
            return id_
        except Exception as e:
            logging.error(f"Error during set category: {e}", exc_info=True)
            raise e

    def delete_category(self, id):
        db = Database()
        try:
            db.delete_category(id)
        except Exception as e:
            logging.error(f"Error during delete category: {e}", exc_info=True)
            raise e

    def fetch_all_categories(self):
        db = Database()
        try:
            categories = db.fetch_all_categories()
            return categories
        except Exception as e:
            logging.error(f"Error during fetch categories: {e}", exc_info=True)
            return []

    def fetch_category_by_name(self, category_name):
        db = Database()
        try:
            category = db.fetch_category_by_name(category_name)
            return category
        except Exception as e:
            logging.error(
                f"Error during fetch category by name: {e}", exc_info=True)
            return []

    def fetch_subcategory_by_name(self, subcategory_name):
        db = Database()
        try:
            subcategory = db.fetch_subcategory_by_name(subcategory_name)
            return subcategory
        except Exception as e:
            logging.error(
                f"Error during fetch subcategory by name: {e}", exc_info=True)
            return []

    def get_subcategory_name(self, subcategory_id):
        subc_name = None
        is_numeric = False

        if isinstance(subcategory_id, int):
            is_numeric = True

        if isinstance(subcategory_id, str) and subcategory_id.isdigit():
            is_numeric = True

        if is_numeric:
            subc_name = self.fetch_subcategory(int(subcategory_id))[2]
        else:
            subc_name = str(
                subcategory_id) if subcategory_id is not None else "Otros"

        return subc_name

    def get_category_name(self, category_id):
        category_name = None
        is_numeric = False
        if isinstance(category_id, int):
            is_numeric = True

        if isinstance(category_id, str) and category_id.isdigit():
            is_numeric = True

        if is_numeric:
            category_name = self.fetch_category(int(category_id))
            if category_name is None:
                return "Categoría no encontrada"

            return category_name[1]
        else:
            category_name = str(category_id) if category_id is not None else ""

        return category_name

    def fetch_category(self, id):
        db = Database()
        try:
            category = db.fetch_category(id)
            return category
        except Exception as e:
            logging.error(f"Error during fetch category: {e}", exc_info=True)
            return None

    def update_category(self, id, name, description):
        db = Database()
        try:
            db.update_category(id, name, description)
        except Exception as e:
            logging.error(f"Error during update category: {e}", exc_info=True)
            raise e

    def delete_all_categories(self):
        db = Database()
        try:
            db.delete_all_categories()
            return True
        except Exception as e:
            logging.error(
                f"Error during delete all categories: {e}", exc_info=True)
            return False

    def deactivate_category(self, id):
        db = Database()
        try:
            db.deactivate_category(id)
        except Exception as e:
            logging.error(f"Error during deactivate categories {e}")

    def activate_category(self, id):
        db = Database()
        db.activate_category(id)

    def fetch_subcategory(self, id):
        db = Database()
        try:
            subcategory = db.fetch_subcategory(id)
            return subcategory
        except Exception as e:
            logging.error(
                f"Error during fetch subcategory: {e}", exc_info=True)
            return None

    def fetch_all_subcategories(self):
        db = Database()
        try:
            subcategories = db.fetch_all_subcategories()
            return subcategories
        except Exception as e:
            logging.error(
                f"Error during fetch subcategories: {e}", exc_info=True)
            return []

    def set_subcategory(self, category_id, name, description=""):
        db = Database()
        try:
            id_ = db.set_subcategory(category_id, name, description)
            return id_
        except Exception as e:
            logging.error(f"Error during set subcategory: {e}", exc_info=True)
            raise e

    def fetch_subcategories(self, category_id):
        db = Database()
        try:
            subcategories = db.fetch_subcategories(category_id)
            return subcategories
        except Exception as e:
            logging.error(
                f"Error during fetch subcategories: {e}", exc_info=True)
            return []

    def delete_subcategory(self, id):
        db = Database()
        try:
            db.delete_subcategory(id)
        except Exception as e:
            logging.error(
                f"Error during delete subcategory: {e}", exc_info=True)
            raise e

    def update_subcategory(self, id, name, description):
        db = Database()
        try:
            db.update_subcategory(id, name, description)
        except Exception as e:
            logging.error(
                f"Error during update subcategory: {e}", exc_info=True)
            raise e

    def deactivate_subcategory(self, id):
        db = Database()
        try:
            db.deactivate_subcategory(id)
        except Exception as e:
            logging.error(
                f"Error during deactivate subcategory {e}", exc_info=True)
            raise e

    def activate_subcategory(self, id):
        db = Database()
        try:
            db.activate_subcategory(id)
        except Exception as e:
            logging.error(
                f"Error during activate subcategory {e}", exc_info=True)
            raise e

    def get_category_by_subcategory_id(self, subcategory_id):
        """Obtiene el ID de la categoría mediante el ID de la subcategoría"""
        db = Database()
        try:
            return db.fetch_category_by_subcategory_id(subcategory_id)
        except Exception as e:
            logging.error(f"Error fetching category id: {e}", exc_info=True)
            return None
