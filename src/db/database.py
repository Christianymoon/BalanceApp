from db.db_connection import conn
from db.migrate import make_migrations
from dto.transactions import TransactionOutputDTO


def normalize_date(d):
    if not d:
        return None
    d_str = str(d).strip()
    if len(d_str) >= 10 and d_str[4] == '-' and d_str[7] == '-':
        return d_str[:10]
    if len(d_str) >= 10 and d_str[2] == '/' and d_str[5] == '/':
        parts = d_str[:10].split('/')
        return f"{parts[2]}-{parts[1]}-{parts[0]}"
    return d_str


class Database:

    def create_tables(self):
        make_migrations(conn)

    def drop_tables(self):
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS passive")
        cursor.execute("DROP TABLE IF EXISTS active")
        cursor.execute("DROP TABLE IF EXISTS transactions")
        cursor.execute("DROP TABLE IF EXISTS balance")
        cursor.execute("DROP TABLE IF EXISTS liquid")
        cursor.execute("DROP TABLE IF EXISTS borrowings")
        cursor.execute("DROP TABLE IF EXISTS intertransactions")
        cursor.execute("DROP TABLE IF EXISTS categories")
        cursor.execute("DROP TABLE IF EXISTS subcategories")
        cursor.execute("DROP TABLE IF EXISTS schema_migrations")
        cursor.execute("DROP TABLE IF EXISTS balance_snapshots")
        conn.commit()
        cursor.close()

    # TRANSACTIONS

    def set_transaction(self, name, category, price, is_income, expense_percentage, subcategory, created_at=None):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (name, category, price, is_income, expense_percentage, subcategory, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name, category, price, is_income, expense_percentage, subcategory, created_at))
        conn.commit()
        cursor.close()

    def fetch_transactions(self, filter):
        cursor = conn.cursor()
        sql = """
            SELECT * FROM transactions 
            WHERE 1 = 1 
        """
        params = []

        if filter.date_to and filter.date_from:
            date_from = normalize_date(filter.date_from)
            date_to = normalize_date(filter.date_to)
            sql += """ AND (
                CASE 
                    WHEN created_at LIKE '__/__/____%' THEN substr(created_at, 7, 4) || '-' || substr(created_at, 4, 2) || '-' || substr(created_at, 1, 2)
                    ELSE substr(created_at, 1, 10)
                END BETWEEN ? AND ?
            )"""
            params.append(date_from)
            params.append(date_to)

        if filter.category_id:
            sql += " AND category = ?"
            params.append(filter.category_id)

        if filter.subcategory_id:
            sql += " AND subcategory = ?"
            params.append(filter.subcategory_id)

        if filter.is_income is not None:
            sql += " AND is_income = ?"
            params.append(filter.is_income)

        sql += " ORDER BY id DESC"

        if filter.limit:
            sql += " LIMIT ?"
            params.append(filter.limit)

        cursor.execute(sql, params)
        result = cursor.fetchall()
        cursor.close()
        return [TransactionOutputDTO(t[0], t[1], t[2], t[7], t[3], t[4], t[5], t[6]) for t in result]

    def fetch_summary(self, filter):
        cursor = conn.cursor()
        sql = """
            SELECT SUM(price) FROM transactions 
            WHERE 1 = 1 
        """
        params = []

        if filter.date_to and filter.date_from:
            date_from = normalize_date(filter.date_from)
            date_to = normalize_date(filter.date_to)
            sql += """ AND (
                CASE 
                    WHEN created_at LIKE '__/__/____%' THEN substr(created_at, 7, 4) || '-' || substr(created_at, 4, 2) || '-' || substr(created_at, 1, 2)
                    ELSE substr(created_at, 1, 10)
                END BETWEEN ? AND ?
            )"""
            params.append(date_from)
            params.append(date_to)

        if filter.category_id:
            sql += " AND category = ?"
            params.append(filter.category_id)

        if filter.subcategory_id:
            sql += " AND subcategory = ?"
            params.append(filter.subcategory_id)

        if filter.is_income is not None:
            sql += " AND is_income = ?"
            params.append(filter.is_income)

        sql += " ORDER BY created_at DESC"

        if filter.limit:
            sql += " LIMIT ?"
            params.append(filter.limit)

        cursor.execute(sql, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def update_transaction(self, id, name, category, price, is_income, expense_percentage, subcategory):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE transactions
            SET name = ?, category = ?, price = ?, is_income = ?, expense_percentage = ?, subcategory = ?
            WHERE id = ?
        """, (name, category, price, is_income, expense_percentage, subcategory, id))
        conn.commit()
        cursor.close()

    def delete_all_transactions(self):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        conn.commit()
        cursor.close()

    # CATEGORIES

    def set_category(self, name, description=None):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO categories (name, description)
            VALUES (?, ?)
        """, (name, description))
        conn.commit()
        cursor.close()
        return cursor.lastrowid

    def fetch_all_categories(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY id DESC")
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_category(self, id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE id = ?", (id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_category_by_subcategory_id(self, subcategory_id):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.id, c.name
            FROM categories c
            JOIN subcategories sc ON c.id = sc.category_id
            WHERE sc.id = ?
        """, (subcategory_id,))
        result = cursor.fetchone()
        cursor.close()
        return result if result else None

    def update_category(self, id, name, description):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE categories
            SET name = ?, description = ?
            WHERE id = ?
        """, (name, description, id))
        conn.commit()
        cursor.close()

    def deactivate_category(self, id):
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE categories
                SET is_active = 0 
                WHERE id = ?""", (id,))
            cursor.execute("""UPDATE subcategories
                SET is_active = 0 
                WHERE category_id = ?""", (id,))
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def activate_category(self, id):
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE categories
                SET is_active = 1
                WHERE id = ?""", (id,))
            cursor.execute("""
                UPDATE subcategories
                SET is_active = 1
                WHERE category_id = ?""", (id,))
            conn.commit()
        except:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def delete_all_categories(self):
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM categories")
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    # SUBCATEGORIES

    def set_subcategory(self, category_id, name, description=""):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO subcategories (category_id, name, description)
            VALUES (?, ?, ?)
        """, (category_id, name, description))
        conn.commit()
        subcategory_id = cursor.lastrowid
        cursor.close()
        return subcategory_id

    def fetch_subcategories(self, category_id):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM subcategories
            WHERE category_id = ?
            ORDER BY id DESC
        """, (category_id,))
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_subcategory(self, subcategory_id):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM subcategories WHERE id = ?", (subcategory_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all_subcategories(self):
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
            s.id,
            s.category_id,
            s.name,
            s.is_active,
            c.name AS category_name 
            FROM subcategories s 
            INNER JOIN categories c ON s.category_id = c.id WHERE s.is_active = 1
            ORDER BY c.id DESC
        """)
        result = cursor.fetchall()
        cursor.close()
        return result

    def update_subcategory(self, id, name, description):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE subcategories
            SET name = ?, description = ?
            WHERE id = ?
        """, (name, description, id))
        conn.commit()
        cursor.close()

    def deactivate_subcategory(self, id):
        cursor = conn.cursor()
        cursor.execute("""UPDATE subcategories
            SET is_active = 0 WHERE id = ?""", (id,))
        conn.commit()
        cursor.close()

    def activate_subcategory(self, id):
        cursor = conn.cursor()
        try:
            cursor.execute("""UPDATE subcategories
                SET is_active = 1 WHERE id = ?""", (id,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()

    # INTERTRANSACTIONS

    def set_intertransaction(self, source_name, source_dest, total, created_at=None):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO intertransactions (source_name, source_dest, total, created_at)
            VALUES (?, ?, ?, ?)
        """, (source_name, source_dest, total, created_at))
        conn.commit()
        cursor.close()

    def fetch_intertransactions(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM intertransactions")
        result = cursor.fetchall()
        cursor.close()
        return result

    # BALANCE

    def set_balance(self, total_balance):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO balance (total_balance)
            VALUES (?)
        """, (total_balance,))
        conn.commit()
        cursor.close()

    def fetch_balance(self):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM balance ORDER BY last_updated DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result

    def update_atomic_balance(self, amount):
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE balance
                SET total_balance = total_balance + ?
                WHERE id = (SELECT id FROM balance ORDER BY last_updated DESC LIMIT 1)
        """, (amount, ))
        conn.commit()
        cursor.close()

    # PASSIVES

    def set_passive(self, name, category, price, is_liquidated, created_at=None):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO passive (name, category, price, is_liquidated, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, price, is_liquidated, created_at))
        conn.commit()
        cursor.close()

    def fetch_passives(self, order_by="price"):
        allowed_columns = ["name", "category",
                           "price", "is_liquidated", "created_at"]
        if order_by not in allowed_columns:
            raise ValueError(f"Invalid column name {order_by}")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM passive ORDER BY {order_by} DESC")
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_passive(self, id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM passive WHERE id = ?", (id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def update_passive(self, id):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE passive
            SET is_liquidated = 1
            WHERE id = ?
        """, (id,))
        conn.commit()
        cursor.close()

    def delete_passive(self, id):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passive WHERE id = ?", (id,))
        conn.commit()
        cursor.close()

    # ACTIVES

    def set_active(self, active_type, name, mount, is_liquid):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO active (active_type, name, mount, is_liquid)
            VALUES (?, ?, ?, ?)
        """, (active_type, name, mount, is_liquid))
        conn.commit()
        active_id = cursor.lastrowid
        cursor.close()
        return active_id

    def fetch_active(self, id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM active WHERE id = ?", (id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all_actives(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM active ORDER BY is_liquid = 1 ASC")
        result = cursor.fetchall()
        cursor.close()
        return result

    def update_active(self, id, amount):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE active
            SET mount = ?
            WHERE id = ?
        """, (amount, id))
        conn.commit()
        cursor.close()

    def delete_active(self, id):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM active WHERE id = ?", (id,))
        conn.commit()
        cursor.close()

    # LIQUID

    def set_liquid(self, amount):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO liquid (amount)
            VALUES (?)
        """, (amount,))
        conn.commit()
        cursor.close()

    def fetch_liquid(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM liquid ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result

    def udpate_liquid(self, amount):
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE liquid
                SET amount = amount + ?
                WHERE id = (SELECT id FROM liquid ORDER BY created_at DESC LIMIT 1)
        """, (amount, ))
        conn.commit()
        cursor.close()

    # USERDATA

    def set_userdata(self, username, gender=None):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO userdata (username, gender)
            VALUES (?, ?)""", (username, gender))
        conn.commit()
        cursor.close()

    def fetch_userdata(self):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM userdata ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result

    # BORROWINGS

    def set_borrowing(self, active_id, name, amount, interest, total_paylable, created_at=None):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO borrowings (active_id, name, amount, interest, total_paylable, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (active_id, name, amount, interest, total_paylable, created_at))
        conn.commit()
        cursor.close()

    def fetch_borrowings(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM borrowings ORDER BY created_at DESC")
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_one_borrowing(self, id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM borrowings WHERE id = ?", (id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    def paid_loan(self, id):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE borrowings
            SET is_paid = 1
            WHERE id = ?
        """, (id,))
        conn.commit()
        cursor.close()

    def delete_borrowing(self, id):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM borrowings WHERE id = ?", (id,))
        conn.commit()
        cursor.close()

    # BALANCE SNAPSHOTS

    def make_snapshot(self, balance, created_at=None):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO balance_snapshots (balance, created_at)
            VALUES (?, ?)
        """, (balance, created_at))
        conn.commit()
        cursor.close()

    def fetch_balance_snapshots(self):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM balance_snapshots ORDER BY created_at ASC")
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_last_date_snapshot(self):
        cursor = conn.cursor()
        cursor.execute(
            "SELECT created_at FROM balance_snapshots ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else None
