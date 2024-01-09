-- THIS CODE FOR INITIALIZE
-- JUST COPY TO YOUR SQL AND RUN IT

CREATE DATABASE sportiton;
USE sportiton;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    age INT,
    interest VARCHAR(50)
);
CREATE TABLE courts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    type VARCHAR(50),
    location VARCHAR(50)
);