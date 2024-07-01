
# Bookstore Project

This is a Flask-based RESTful API for managing a bookstore. The application supports user registration, login, and book management operations such as adding, viewing, and deleting books. 

It uses JWT for authentication, SQLAlchemy for database operations, and Flask-Swagger for API documentation.

## Features

- User registration and login with JWT authentication.
- CRUD operations for books.
- SQLAlchemy for database interactions.
- Swagger for API documentation.

## Technologies Used

- Python
- Flask
- SQLAlchemy
- JWT
- SQLite (for local development)
- Swagger (Flasgger)

## Installation

### Prerequisites

- Python 3.7 or higher
- `pip` package manager

### Steps

1. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/bookstore-project.git
    cd bookstore-project
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:

    ```bash
    python app.py
    ```

    The application should now be running at `http://127.0.0.1:5000/`.

## API Endpoints

### User Registration

**Endpoint:** `/register`  
**Method:** `POST`  
**Description:** Registers a new user.

**Request Body:**

```json
{
  "name": "string",
  "password": "string"
}
```

## API Endpoints

### Get All Books

- **Endpoint:** `/books`
- **Method:** `GET`
- **Description:** Retrieves all books for the logged-in user.

**Headers:**

- `x-access-tokens: <JWT token>`

**Responses:**

- `200 OK`: List of all books.

### Get Book by Name

- **Endpoint:** `/books/<name>`
- **Method:** `GET`
- **Description:** Retrieves a book by its name.

**Headers:**

- `x-access-tokens: <JWT token>`

**Responses:**

- `200 OK`: Book details retrieved successfully.
- `404 Not Found`: Book not found.

### Delete Book

- **Endpoint:** `/books/<book_id>`
- **Method:** `DELETE`
- **Description:** Deletes a book by its ID.

**Headers:**

- `x-access-tokens: <JWT token>`

**Responses:**

- `200 OK`: Book deleted successfully.
- `401 Unauthorized`: Token is missing or invalid.
- `404 Not Found`: Book not found.

## Running Tests

To run the unit tests, use the following command:

```bash
python test_main.py

