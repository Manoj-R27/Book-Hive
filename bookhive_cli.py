import mysql.connector
from tabulate import tabulate


# -------------------- DATABASE --------------------
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="@Password0",  # change to your MySQL password
        database="BookHiveDB"
    )


# -------------------- COMMON UTIL --------------------
def execute_query(cursor, query, params=None, fetch=False):
    cursor.execute(query, params or ())
    if fetch:
        return cursor.fetchall()


def exists_user(cursor, uid):
    cursor.execute("SELECT 1 FROM Users WHERE UserID=%s", (uid,))
    return cursor.fetchone() is not None


def exists_transaction(cursor, tid):
    cursor.execute("SELECT 1 FROM LendingTransaction WHERE TransactionID=%s", (tid,))
    return cursor.fetchone() is not None


# -------------------- ADMIN LOGIN --------------------
def admin_login():
    username = input("Enter admin username: ")
    password = input("Enter admin password: ")
    if username == "admin" and password == "admin123":
        print("\nAdmin login successful.\n")
        return True
    print("\nInvalid credentials.\n")
    return False


# -------------------- ADMIN FUNCTIONS --------------------
def add_user(cursor, db):
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone: ")
    address = input("Enter Address: ")
    cursor.execute(
        "INSERT INTO Users (Name, Email, Phone, Address, JoinDate) VALUES (%s, %s, %s, %s, NOW())",
        (name, email, phone, address)
    )
    db.commit()
    print("\nUser added successfully.\n")


def add_book(cursor, db):
    title = input("Enter Title: ")
    author = input("Enter Author: ")
    genre = input("Enter Genre: ")
    isbn = input("Enter ISBN: ")
    owner = input("Enter OwnerID: ")
    cursor.execute(
        "INSERT INTO Book (Title, Author, Genre, ISBN, AvailabilityStatus, OwnerID) VALUES (%s, %s, %s, %s, 'Available', %s)",
        (title, author, genre, isbn, owner)
    )
    db.commit()
    print("\nBook added successfully.\n")


def update_user(cursor, db):
    uid = input("Enter UserID to update: ")
    name = input("Enter new name: ")
    email = input("Enter new email: ")
    phone = input("Enter new phone: ")
    address = input("Enter new address: ")
    cursor.execute(
        "UPDATE Users SET Name=%s, Email=%s, Phone=%s, Address=%s WHERE UserID=%s",
        (name, email, phone, address, uid)
    )
    db.commit()
    print("\nUser updated successfully.\n")


def update_book(cursor, db):
    bid = input("Enter BookID to update: ")
    title = input("Enter new title: ")
    author = input("Enter new author: ")
    genre = input("Enter new genre: ")
    isbn = input("Enter new ISBN: ")
    status = input("Enter new status (Available/Lent/Reserved): ")
    owner = input("Enter new OwnerID: ")
    cursor.execute(
        "UPDATE Book SET Title=%s, Author=%s, Genre=%s, ISBN=%s, AvailabilityStatus=%s, OwnerID=%s WHERE BookID=%s",
        (title, author, genre, isbn, status, owner, bid)
    )
    db.commit()
    print("\nBook updated successfully.\n")


def delete_user(cursor, db):
    uid = input("Enter UserID to delete: ")
    cursor.execute("DELETE FROM Users WHERE UserID=%s", (uid,))
    db.commit()
    print("\nUser deleted successfully.\n")


def delete_book(cursor, db):
    bid = input("Enter BookID to delete: ")
    cursor.execute("DELETE FROM Book WHERE BookID=%s", (bid,))
    db.commit()
    print("\nBook deleted successfully.\n")


def view_all(cursor, table, headers):
    try:
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        if rows:
            print(tabulate(rows, headers=headers, tablefmt="psql"))
        else:
            print(f"\nNo data found in {table}.\n")
    except Exception as e:
        print(f"\nError retrieving data from {table}: {e}\n")


# -------------------- USER FUNCTIONS --------------------
def show_users(cursor):
    cursor.execute("SELECT UserID, Name, Email, Phone FROM Users")
    rows = cursor.fetchall()
    print(tabulate(rows, headers=["UserID", "Name", "Email", "Phone"], tablefmt="psql"))


def show_books(cursor):
    cursor.execute("SELECT BookID, Title, Author, Genre, AvailabilityStatus FROM Book")
    rows = cursor.fetchall()
    print(tabulate(rows, headers=["BookID", "Title", "Author", "Genre", "Status"], tablefmt="psql"))


def check_availability(cursor):
    bid = input("Enter BookID: ")
    cursor.execute("SELECT IsBookAvailable(%s) AS Status", (bid,))
    res = cursor.fetchone()
    print(f"\nBook {bid} is currently: {res[0]}")


def borrow_book(cursor, db):
    borrower = input("Enter your UserID: ")
    bid = input("Enter BookID to borrow: ")
    
    # Fetch OwnerID to avoid trigger conflict
    cursor.execute("SELECT OwnerID FROM Book WHERE BookID=%s", (bid,))
    owner = cursor.fetchone()
    if owner is None:
        print("\nBook not found.\n")
        return
    owner_id = owner[0]

    # Validate borrower exists
    if not exists_user(cursor, borrower):
        print(f"\nBorrower UserID {borrower} does not exist. Please provide a valid UserID.\n")
        return

    # Insert new lending transaction
    try:
        cursor.execute("""
            INSERT INTO LendingTransaction (BookID, LenderID, BorrowerID, IssueDate, DueDate, Status)
            VALUES (%s, %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'Issued')
        """, (bid, owner_id, borrower))
        db.commit()
    except Exception as e:
        print(f"\nFailed to create lending transaction: {e}\n")
        return

    # Get last inserted TransactionID
    transaction_id = cursor.lastrowid
    print(f"\nBook borrowed successfully. Transaction ID: {transaction_id}\n")




def return_book(cursor, db):
    tid = input("Enter TransactionID: ")
    cursor.execute(
        "UPDATE LendingTransaction SET Status='Returned', ReturnDate=CURDATE() WHERE TransactionID=%s", (tid,)
    )
    db.commit()
    print("\nBook returned successfully.\n")


def view_pending_requests(cursor):
    cursor.execute(
        """
        SELECT r.RequestID, u.Name AS Requester, b.Title, r.Status
        FROM Request r
        JOIN Users u ON r.RequesterID = u.UserID
        JOIN Book b ON r.BookID = b.BookID
        WHERE r.Status='Pending'
        """
    )
    rows = cursor.fetchall()
    print(tabulate(rows, headers=["RequestID", "Requester", "Book", "Status"], tablefmt="psql"))


def rate_user(cursor, db):
    tid = input("Enter TransactionID: ")
    rater = input("Your UserID: ")
    ratee = input("Ratee UserID: ")
    stars = input("Stars (1-5): ")
    comment = input("Comment: ")
    # Validate inputs
    if not exists_transaction(cursor, tid):
        print(f"\nTransactionID {tid} does not exist.\n")
        return
    if not exists_user(cursor, rater):
        print(f"\nRater UserID {rater} does not exist.\n")
        return
    if not exists_user(cursor, ratee):
        print(f"\nRatee UserID {ratee} does not exist.\n")
        return

    try:
        stars_int = int(stars)
        if stars_int < 1 or stars_int > 5:
            print("\nStars must be between 1 and 5.\n")
            return
    except ValueError:
        print("\nInvalid stars value. Enter an integer between 1 and 5.\n")
        return

    try:
        cursor.execute(
            """
            INSERT INTO Rating (TransactionID, RaterID, RateeID, Stars, Comment)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (tid, rater, ratee, stars_int, comment)
        )
        db.commit()
        print("\nRating submitted successfully.\n")
    except Exception as e:
        # Common causes: Rating table not configured with AUTO_INCREMENT for RatingID
        print(f"\nFailed to submit rating: {e}\n")
        print("If the error mentions 'RatingID', run this SQL to fix the table:\n")
        print("ALTER TABLE Rating MODIFY RatingID INT NOT NULL AUTO_INCREMENT;\n")


def user_average_rating(cursor):
    uid = input("Enter UserID: ")
    cursor.execute("SELECT GetUserAverageRating(%s)", (uid,))
    res = cursor.fetchone()
    print(f"\nAverage Rating for User {uid}: {res[0]}\n")


# -------------------- MENUS --------------------
def admin_menu(cursor, db):
    while True:
        print(
            """
================ ADMIN MENU ================
1. Add User
2. Add Book
3. Update User
4. Update Book
5. Delete User
6. Delete Book
7. View Users
8. View Books
9. View Requests
10. View Transactions
11. View Ratings
12. Logout
============================================
        """
        )
        choice = input("Enter choice: ")

        if choice == '1':
            add_user(cursor, db)
        elif choice == '2':
            add_book(cursor, db)
        elif choice == '3':
            update_user(cursor, db)
        elif choice == '4':
            update_book(cursor, db)
        elif choice == '5':
            delete_user(cursor, db)
        elif choice == '6':
            delete_book(cursor, db)
        elif choice == '7':
            view_all(cursor, "Users", ["UserID", "Name", "Email", "Phone", "Address", "JoinDate"])
        elif choice == '8':
            view_all(cursor, "Book", ["BookID", "Title", "Author", "Genre", "ISBN", "AvailabilityStatus", "OwnerID"])
        elif choice == '9':
            view_all(cursor, "Request", ["RequestID", "BookID", "RequesterID", "RequestDate", "Status"])
        elif choice == '10':
            view_all(cursor, "LendingTransaction", ["TransactionID", "BookID", "BorrowerID", "LenderID", "IssueDate", "DueDate", "ReturnDate", "Status"])
        elif choice == '11':
            view_all(cursor, "Rating", ["RatingID", "TransactionID", "RaterID", "RateeID", "Stars", "Comment"])
        elif choice == '12':
            print("\nLogged out.\n")
            break
        else:
            print("\nInvalid choice.\n")


def user_menu(cursor, db):
    while True:
        print(
            """
================ USER MENU ================
1. Show all users
2. Show all books
3. Check book availability
4. Borrow a book
5. Return a book
6. View pending requests
7. Rate a user
8. View user average rating
9. Exit
===========================================
        """
        )
        choice = input("Enter choice: ")

        if choice == '1':
            show_users(cursor)
        elif choice == '2':
            show_books(cursor)
        elif choice == '3':
            check_availability(cursor)
        elif choice == '4':
            borrow_book(cursor, db)
        elif choice == '5':
            return_book(cursor, db)
        elif choice == '6':
            view_pending_requests(cursor)
        elif choice == '7':
            rate_user(cursor, db)
        elif choice == '8':
            user_average_rating(cursor)
        elif choice == '9':
            print("\nGoodbye.\n")
            break
        else:
            print("\nInvalid choice.\n")


# -------------------- MAIN --------------------
def main():
    db = connect_db()
    cursor = db.cursor()

    print("\nWelcome to BookHive CLI")
    mode = input("Login as (admin/user): ").strip().lower()

    if mode == "admin":
        if admin_login():
            admin_menu(cursor, db)
    elif mode == "user":
        user_menu(cursor, db)
    else:
        print("\nInvalid role.\n")

    cursor.close()
    db.close()


if __name__ == "__main__":
    main()
