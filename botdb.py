import sqlite3

class botdb:
    def __init__(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cur = self.conn.cursor()

    def get_all_userid(self):
        result = self.cur.execute("SELECT user_id FROM users")
        return result.fetchall()

    def get_id(self, user_id):
        result = self.cur.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
        return result.fetchone()[0]

    def get_user_id(self, mention):
        result = self.cur.execute("SELECT user_id FROM users WHERE user_mention = ?", (mention,))
        return result.fetchone()[0]

    def get_id_mention(self, mention):
        result = self.cur.execute("SELECT id FROM users WHERE user_mention = ?", (mention,))
        return result.fetchone()[0]

    def get_ref(self, user_id):
        result = self.cur.execute("Select ref_id from users where user_id = ?", (user_id,))
        return result.fetchone()[0]

    def get_regdate(self, user_id):
        result = self.cur.execute("Select join_date from users where user_id = ?", (user_id,))
        return result.fetchone()[0]

    def user_exists(self, user_id):
        result = self.cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        return bool(len(result.fetchall()))

    def new_user(self, user_id, user_mention, ref_code):
        user = (user_id, user_mention, 1000, False, ref_code)
        self.cur.execute('''INSERT INTO 'users' ('user_id', 'user_mention', 'balance', 'admin', 'ref_id') VALUES (?, ?, ?, ?, ?)''', (user))
        return self.conn.commit()

    def check_balance(self, user_id):
        result = self.cur.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        tv = result.fetchone()
        tv = tv[0]
        return tv

    def check_ref_balance(self, user_id):
        result = self.cur.execute("SELECT ref_balance FROM users WHERE user_id = ?", (user_id,))
        tv = result.fetchone()
        tv = tv[0]
        return tv

    def check_admin(self, user_id):
        result = self.cur.execute("SELECT admin FROM users WHERE user_id = ?", (user_id,))
        tv = result.fetchone()
        tv = tv[0]
        return bool(tv)

    def change_balance(self, user_id, summa):
        if self.user_exists(user_id) == True:
            new_summa = self.check_balance(user_id) + summa
            updateask = "Update users set balance = ? where user_id = ?"
            data = (new_summa, user_id)
            self.cur.execute(updateask, data)
            return self.conn.commit()
        else:
            return

    def change_ref_balance(self, user_id, summa):
        if self.user_exists(user_id) == True:
            new_summa = self.check_ref_balance(user_id) + summa
            updateask = "Update users set ref_balance = ? where user_id = ?"
            data = (new_summa, user_id)
            self.cur.execute(updateask, data)
            return self.conn.commit()
        else:
            return

    def change_balance_min(self, user_id, summa):
        if self.user_exists(user_id) == True:
            new_summa = self.check_balance(user_id) - summa
            updateask = "Update users set balance = ? where user_id = ?"
            data = (new_summa, user_id)
            self.cur.execute(updateask, data)
            return self.conn.commit()
        else:
            return

    def adm_minus_ref(self, user_id, value):
        if self.user_exists(user_id) == True:
            new_summa = self.check_ref_balance(user_id) - value
            updateask = "Update users set ref_balance = ? where user_id = ?"
            data = (new_summa, user_id)
            self.cur.execute(updateask, data)
            return self.conn.commit()
        else:
            return

    def new_payment(self, user_id, value):
        users_id = botdb.get_id(self, user_id)
        payment = (users_id, value)
        self.cur.execute('''INSERT INTO 'payments' ('users_id', 'value') VALUES (?, ?)''', (payment))
        return self.conn.commit()

    def adm_change_balance(self, user_id, value):
        if self.user_exists(user_id) == True:
            new_summa = self.check_balance(user_id) + value
            updateask = "Update users set balance = ? where user_id = ?"
            data = (new_summa, user_id)
            self.cur.execute(updateask, data)
            return self.conn.commit()
        else:
            return

    def ref_num(self, ref_id):
        result = self.cur.execute('Select ref_id from users where ref_id = ?', (ref_id,))
        return len(result.fetchall())

    def get_price(self, good):
        result = self.cur.execute("Select price from goods where name = ?", (good,))
        return result.fetchone()[0]

    def get_optprice1(self, good):
        result = self.cur.execute("Select opt_price1 from goods where name = ?", (good,))
        return result.fetchone()[0]

    def get_optprice2(self, good):
        result = self.cur.execute("Select opt_price2 from goods where name = ?", (good,))
        return result.fetchone()[0]

    def get_opt1(self, good):
        result = self.cur.execute("Select opt_num1 from goods where name = ?", (good,))
        return result.fetchone()[0]

    def get_opt2(self, good):
        result = self.cur.execute("Select opt_num2 from goods where name = ?", (good,))
        return result.fetchone()[0]





