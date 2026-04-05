import sqlite3

def check_users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, role, department FROM users")
    users = cursor.fetchall()
    print("USER STORE CONTENTS:")
    for user in users:
        print(f"User: {user[0]}, Role: {user[1]}, Dept: {user[2]}")
    conn.close()

if __name__ == "__main__":
    check_users()
