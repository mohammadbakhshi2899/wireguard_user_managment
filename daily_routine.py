from db_functions import daily_routine, remove_expired_users
import shutil

# This script should run separately from the main bot.py.
# Using systemctl's timer.


def main():
    with open('delete_users', 'w') as fd:
        users = remove_expired_users()
        fd.write(str(users))
        for user in users:
            shutil.rmtree(f'users/{user[0]}')
    daily_routine()


if __name__ == '__main__':
    main()
