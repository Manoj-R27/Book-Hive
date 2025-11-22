USE BookHiveDB;

#trigger
#Create a trigger to automatically update the AvailabilityStatus of a book to 'Lent' when a lending transaction is inserted.

DELIMITER $$
CREATE TRIGGER trg_update_book_status
AFTER INSERT ON LendingTransaction
FOR EACH ROW
BEGIN
    UPDATE Book
    SET AvailabilityStatus = 'Lent'
    WHERE BookID = NEW.BookID;
END$$
DELIMITER ;
  
#Automatically set the book’s AvailabilityStatus to 'Available' when a book is returned.
DELIMITER $$

CREATE TRIGGER trg_update_book_status_after_update
AFTER UPDATE ON LendingTransaction
FOR EACH ROW
BEGIN
    IF NEW.Status = 'Returned' THEN
        UPDATE Book
        SET AvailabilityStatus = 'Available'
        WHERE BookID = NEW.BookID;
    END IF;
END$$

DELIMITER ;

#Prevent inserting a lending transaction if the book is not available.
DELIMITER $$

CREATE TRIGGER trg_prevent_lending_unavailable
BEFORE INSERT ON LendingTransaction
FOR EACH ROW
BEGIN
    DECLARE availability ENUM('Available','Lent','Reserved');
    SELECT AvailabilityStatus INTO availability FROM Book WHERE BookID = NEW.BookID;
    IF availability <> 'Available' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Book is not available for lending!';
    END IF;
END$$

DELIMITER ;





#procedure
#Create a procedure to fetch all books currently lent by a particular user.

DELIMITER $$
CREATE PROCEDURE GetLentBooksByUser(IN p_userID INT)
BEGIN
    SELECT b.BookID, b.Title, b.Author, lt.IssueDate, lt.DueDate
    FROM LendingTransaction lt
    JOIN Book b ON lt.BookID = b.BookID
    WHERE lt.LenderID = p_userID AND lt.Status = 'Issued';
END$$

DELIMITER ;

#Approve a book request
DELIMITER $$

CREATE PROCEDURE ApproveBookRequest(IN p_requestID INT)
BEGIN
    UPDATE Request
    SET Status = 'Approved'
    WHERE RequestID = p_requestID;
    
    -- Optional: Insert into LendingTransaction automatically when approved
    INSERT INTO LendingTransaction (TransactionID, BookID, LenderID, BorrowerID, IssueDate, DueDate)
    SELECT CONCAT('3', RequestID), BookID, b.OwnerID, RequesterID, NOW(), DATE_ADD(NOW(), INTERVAL 10 DAY)
    FROM Request r
    JOIN Book b ON r.BookID = b.BookID
    WHERE r.RequestID = p_requestID AND r.Status = 'Approved';
    
    UPDATE Book b
    JOIN Request r ON b.BookID = r.BookID
    SET b.AvailabilityStatus = 'Lent'
    WHERE r.RequestID = p_requestID;
END$$

DELIMITER ;

#Get pending requests
DELIMITER $$

CREATE PROCEDURE GetPendingRequests()
BEGIN
    SELECT r.RequestID, u.Name AS Requester, b.Title AS BookTitle, r.RequestDate
    FROM Request r
    JOIN Users u ON r.RequesterID = u.UserID
    JOIN Book b ON r.BookID = b.BookID
    WHERE r.Status = 'Pending';
END$$

DELIMITER ;


#functions
#Create a function to calculate the total number of books currently borrowed by a user.

DELIMITER $$
CREATE FUNCTION GetBorrowedCount(p_userID INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    SELECT COUNT(*) INTO total
    FROM LendingTransaction
    WHERE BorrowerID = p_userID AND Status = 'Issued';
    RETURN total;
END$$

DELIMITER ;


#Average rating received by a user
DELIMITER $$

CREATE FUNCTION GetUserAverageRating(p_userID INT)
RETURNS DECIMAL(3,2)
DETERMINISTIC
BEGIN
    DECLARE avgRating DECIMAL(3,2);
    SELECT AVG(Stars) INTO avgRating
    FROM Rating
    WHERE RateeID = p_userID;
    RETURN IFNULL(avgRating,0);
END$$

DELIMITER ;


#Check if book is available
DELIMITER $$

CREATE FUNCTION IsBookAvailable(p_bookID INT)
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE status VARCHAR(20);
    SELECT AvailabilityStatus INTO status
    FROM Book
    WHERE BookID = p_bookID;
    RETURN status;
END$$

DELIMITER ;
