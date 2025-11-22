CREATE DATABASE IF NOT EXISTS BookHiveDB;
USE BookHiveDB;

CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Phone VARCHAR(15) UNIQUE NOT NULL,
    Address VARCHAR(200) NOT NULL,
    JoinDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO Users (UserID, Name, Email, Phone, Address, JoinDate) VALUES
(1, 'Alice', 'alice@mail.com', '9876543210', 'Bangalore', NOW()),
(2, 'Bob', 'bob@mail.com', '9123456780', 'Chennai', NOW()),
(3, 'Charlie', 'charlie@mail.com', '9988776655', 'Delhi', NOW()),
(4, 'David', 'david@mail.com', '9765432109', 'Mumbai', NOW()),
(5, 'Eva', 'eva@mail.com', '9345678123', 'Hyderabad', NOW());

CREATE TABLE Book (
    BookID INT PRIMARY KEY AUTO_INCREMENT,
    Title VARCHAR(150) NOT NULL,
    Author VARCHAR(100) NOT NULL,
    Genre VARCHAR(50),
    ISBN VARCHAR(20) UNIQUE NOT NULL,
    AvailabilityStatus ENUM('Available','Lent','Reserved') DEFAULT 'Available',
    OwnerID INT NOT NULL,
    FOREIGN KEY (OwnerID) REFERENCES Users(UserID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO Book (BookID, Title, Author, Genre, ISBN, AvailabilityStatus, OwnerID) VALUES
(101, 'DBMS Made Easy', 'Navathe', 'Education', 'ISBN101', 'Available', 1),
(102, 'Python 101', 'Guido', 'Programming', 'ISBN102', 'Available', 2),
(103, 'Data Science Handbook', 'Wes McKinney', 'Education', 'ISBN103', 'Reserved', 1),
(104, 'The Alchemist', 'Paulo Coelho', 'Fiction', 'ISBN104', 'Lent', 3),
(105, 'Clean Code', 'Robert Martin', 'Programming', 'ISBN105', 'Available', 4);

CREATE TABLE Request (
    RequestID INT PRIMARY KEY AUTO_INCREMENT,
    BookID INT NOT NULL,
    RequesterID INT NOT NULL,
    RequestDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Status ENUM('Pending','Approved','Rejected') DEFAULT 'Pending',
    FOREIGN KEY (BookID) REFERENCES Book(BookID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (RequesterID) REFERENCES Users(UserID)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO Request (RequestID, BookID, RequesterID, RequestDate, Status) VALUES
(201, 101, 2, NOW(), 'Pending'),
(202, 102, 3, NOW(), 'Approved'),
(203, 103, 4, NOW(), 'Rejected'),
(204, 104, 1, NOW(), 'Pending'),
(205, 105, 5, NOW(), 'Approved');

CREATE TABLE LendingTransaction (
    TransactionID INT PRIMARY KEY AUTO_INCREMENT,
    BookID INT NOT NULL,
    LenderID INT,
    BorrowerID INT,
    IssueDate DATE NOT NULL,
    DueDate DATE NOT NULL,
    ReturnDate DATE,
    Status ENUM('Issued','Returned','Overdue') DEFAULT 'Issued',
    FOREIGN KEY (BookID) REFERENCES Book(BookID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (LenderID) REFERENCES Users(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (BorrowerID) REFERENCES Users(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO LendingTransaction (TransactionID, BookID, LenderID, BorrowerID, IssueDate, DueDate, ReturnDate, Status) VALUES
(301, 101, 1, 2, '2025-02-01', '2025-02-10', NULL, 'Issued'),
(302, 102, 2, 3, '2025-02-02', '2025-02-12', '2025-02-11', 'Returned'),
(303, 103, 1, 4, '2025-02-03', '2025-02-13', NULL, 'Issued'),
(304, 104, 3, 1, '2025-02-05', '2025-02-15', NULL, 'Issued'),
(305, 105, 4, 5, '2025-02-07', '2025-02-17', NULL, 'Issued');

CREATE TABLE Rating (
    RatingID INT PRIMARY KEY AUTO_INCREMENT,
    TransactionID INT NOT NULL,
    RaterID INT,
    RateeID INT,
    Stars INT CHECK (Stars BETWEEN 1 AND 5),
    Comment VARCHAR(200),
    FOREIGN KEY (TransactionID) REFERENCES LendingTransaction(TransactionID)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (RaterID) REFERENCES Users(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    FOREIGN KEY (RateeID) REFERENCES Users(UserID)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO Rating (RatingID, TransactionID, RaterID, RateeID, Stars, Comment) VALUES
(401, 302, 3, 2, 5, 'Very smooth transaction'),
(402, 302, 2, 3, 4, 'Good borrower'),
(403, 304, 1, 3, 5, 'Helpful lender'),
(404, 301, 2, 1, 4, 'Book in good condition'),
(405, 305, 5, 4, 5, 'Excellent experience');
