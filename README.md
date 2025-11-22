
```
# BookHive – Community Book Sharing and Lending System

## 📌 Project Overview
BookHive is a CLI-based database application that allows users to share, lend, and borrow books within a community. The system manages users, books, borrowing transactions, requests, and ratings using MySQL as the backend database.

---

## 🛠️ Technologies Used
- Python (CLI Interface)
- MySQL (Database)
- VS Code / PyCharm (IDE)
- mysql-connector-python
- tabulate (for table display)

---

## 📂 Project Structure
```

BookHive/
│
├── bookhive_cli.py
├── create_tables.sql
├── triggers_procedures_functions.sql
└── README.md

````

---

## ⚙️ Features

### Admin Features
- Add User
- Add Book
- Update User
- Update Book
- Delete User
- Delete Book
- View Users
- View Books
- View Requests
- View Transactions
- View Ratings

### User Features
- View all users
- View all books
- Check book availability
- Borrow a book
- Return a book
- View pending requests
- Rate a user
- View average rating

---

## 🧑‍💻 How to Run the Project

### Step 1: Create Database
Open MySQL and run:
```sql
CREATE DATABASE BookHiveDB;
USE BookHiveDB;
````

### Step 2: Create Tables

Run all SQL from:

```
create_tables.sql
```

### Step 3: Run Python CLI

Activate virtual environment and run:

```bash
python bookhive_cli.py
```

---

## 🔐 Default Login

### Admin

* Username: `admin`
* Password: `admin123`

### User

Choose “user” option when prompted.

---

## 🔄 Triggers, Procedures & Functions Used

* Triggers

  * Auto update book availability
  * Prevent lending unavailable books

* Stored Procedures

  * GetLentBooksByUser
  * ApproveBookRequest

* Functions

  * GetBorrowedCount
  * GetUserAverageRating
  * IsBookAvailable


---

## 👨‍🎓 Author

Developed by:
Manoj R , Kumarchandra Edupuganti

```

