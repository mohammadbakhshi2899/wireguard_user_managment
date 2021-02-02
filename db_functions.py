import sqlite3
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    conn = sqlite3.connect('proxy_users.sqlite')
    cur = conn.cursor()
except sqlite3.Error as e:
    logger.error('in sqlite3, while opening proxy_users.sqlite')
    exit()


def find_last_id():
    max_id = cur.execute('SELECT max(uid) FROM tb_users').fetchall()[0][0]
    if max_id:
        return max_id
    return 0


def get_expiration_date(user_id):
    cur.execute(f"SELECT expiration FROM tb_users WHERE( user_id={user_id} );")
    date = cur.fetchall()[0][0]
    return date


def add_user(user_id, user_name):
    if user_name is None:
        user_name = 'NULL'

    try:
        cur.execute(f"INSERT INTO tb_users values(NULL, {user_id}, '{user_name}', 30);")
        conn.commit()
        return True
    except:
        # User exist
        return False


# Add users who attempt to register.
def add_tmp_user(user_id, user_name):
    if user_name is None:
        user_name = 'NULL'

    cur.execute(f"INSERT INTO tb_temp_users values(NULL, {user_id}, '{user_name}', 30);")
    conn.commit()


def get_tmp_user(user_id):
    try:
        cur.execute(f"SELECT * FROM tb_temp_users WHERE(user_id={user_id});")
        user = cur.fetchall()[0]
        return user
    except:
        # User not exist
        return None


def check_user_exist(user_id):
    cur.execute(f"SELECT expiration FROM tb_users WHERE( user_id={user_id} );")
    if cur.fetchall():
        return True
    else:
        return False


def check_expired(user_id):
    cur.execute(f"SELECT expiration FROM tb_users WHERE( user_id={user_id} );")
    expiration = cur.fetchall()[0][0]
    if int(expiration) == 0:
        return True
    else:
        return False


def update_user(user_id):
    cur.execute(f'UPDATE tb_users SET expiration=30 WHERE(user_id={user_id}')
    conn.commit()


def get_admin_user_id():
    cur.execute(f'SELECT user_id FROM tb_users WHERE(uid=1);')
    query = cur.fetchall()
    if query is None:
        return None
    return query


def daily_routine():
    cur.execute(f'UPDATE tb_users SET expiration=expiration-1')
    conn.commit()


def remove_expired_users():
    cur.execute('SELECT * FROM tb_users WHERE(expiration=0);')
    users = cur.fetchall()
    cur.execute('DELETE FROM tb_users WHERE(expiration=0);')
    conn.commit()
    return users
