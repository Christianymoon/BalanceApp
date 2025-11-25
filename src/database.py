from db_connection import conn

class Database:

    def create_tables(self):
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS passive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            is_liquidated BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS userdata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            gender TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS balance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_balance REAL NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS active (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            active_type TEXT NOT NULL,
            name TEXT NOT NULL,
            mount REAL NOT NULL,
            is_liquid BOOLEAN NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            is_income BOOLEAN NOT NULL,
            expense_percentage REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS liquid (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        conn.commit()
        cursor.close()
    
    def set_transaction(self, name, category, price, is_income, expense_percentage):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (name, category, price, is_income, expense_percentage)
            VALUES (?, ?, ?, ?, ?)
        """, (name, category, price, is_income, expense_percentage))
        conn.commit()
        cursor.close()

    def set_balance(self, total_balance):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO balance (total_balance)
            VALUES (?)
        """, (total_balance,))
        conn.commit()
        cursor.close()
    

    def set_passive(self, name, category, price, is_liquidated):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO passive (name, category, price, is_liquidated)
            VALUES (?, ?, ?, ?)
        """, (name, category, price, is_liquidated))
        conn.commit()
        cursor.close()

    def set_active(self, active_type, name, mount, is_liquid):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO active (active_type, name, mount, is_liquid)
            VALUES (?, ?, ?, ?)
        """, (active_type, name, mount, is_liquid))
        conn.commit()
        cursor.close()

    def set_liquid(self, amount):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO liquid (amount)
            VALUES (?)
        """, (amount,))
        conn.commit()
        cursor.close()

    def set_userdata(self, username, gender=None):
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO userdata (username, gender)
            VALUES (?, ?)""", (username, gender))
        conn.commit()
        cursor.close()

    def fetch_transactions(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions")
        result = cursor.fetchall()
        cursor.close()
        return result

    def fetch_last_transaction(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_balance(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM balance ORDER BY last_updated DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def fetch_passives(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM passive")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def fetch_active(self, id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM active WHERE id = ?", (id,))
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def fetch_all_actives(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM active")
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def fetch_liquid(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM liquid ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def fetch_userdata(self):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM userdata ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def delete_all_transactions(self):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions")
        conn.commit()
        cursor.close()

    def delete_passive(self, id):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM passive WHERE id = ?", (id,))
        conn.commit()
        cursor.close()

    def delete_active(self, id):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM active WHERE id = ?", (id,))
        conn.commit()
        cursor.close()

    def update_passive(self, id):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE passive
            SET is_liquidated = 1
            WHERE id = ?
        """, (id,))
        conn.commit()
        cursor.close()

    def update_active(self, id, amount):
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE active
            SET mount = ?
            WHERE id = ?
        """, (amount, id))
        conn.commit()
        cursor.close()

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



    def search_passive(self, id):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM passive WHERE id = ?", (id,))
        result = cursor.fetchone()
        cursor.close()
        return result