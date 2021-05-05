DROP TABLE Users;
DROP TABLE Messages;
DROP TABLE SignedInUsers;


CREATE TABLE Users (
    Email varchar(50) NOT NULL,
    Fname varchar(50) NOT NULL,
    Lname varchar(50) NOT NULL,
    Psw varchar(50) NOT NULL,
    Country varchar(50) NOT NULL,
    City varchar(50) NOT NULL,
    Gender varchar(50) NOT NULL,
    primary key(Email)  
);

CREATE TABLE Messages (
    id integer PRIMARY KEY,
    ReceiverEmail varchar(50) NOT NULL,
    SenderEmail varchar(50) NOT NULL,
    Msg varchar(255) NOT NULL,
    City varchar(50) NOT NULL,
    Country varchar(50) NOT NULL,
    SenderGender varchar(50) NOT NULL,
    FOREIGN key (ReceiverEmail) REFERENCES Users(Email),
    FOREIGN key (SenderEmail) REFERENCES Users(Email),
    FOREIGN key (SenderGender) REFERENCES Users(Gender)
);

CREATE TABLE SignedInUsers (
    Email varchar(50) NOT NULL,
    Token varchar(50) NOT NULL,
    PRIMARY key (Token),
    FOREIGN key (Email) REFERENCES Users(Email)
);