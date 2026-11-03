import json
import os

BOOKS_FILE = "books.json"
ISSUED_FILE = "issued_books.json"

books = []
issued_books = []


# ==========================
# FILE HANDLING
# ==========================

def load_data():
    global books, issued_books

    if os.path.exists(BOOKS_FILE):
        with open(BOOKS_FILE, "r") as f:
            books = json.load(f)

    if os.path.exists(ISSUED_FILE):
        with open(ISSUED_FILE, "r") as f:
            issued_books = json.load(f)


def save_data():
    with open(BOOKS_FILE, "w") as f:
        json.dump(books, f, indent=4)

    with open(ISSUED_FILE, "w") as f:
        json.dump(issued_books, f, indent=4)

    print("Data saved successfully.")


# ==========================
# BOOK FUNCTIONS
# ==========================

def add_book():
    book_id = input("Enter Book ID: ")

    for book in books:
        if book["id"] == book_id:
            print("Book ID already exists.")
            return

    title = input("Enter Title: ")
    author = input("Enter Author: ")
    genre = input("Enter Genre: ")
    qty = int(input("Enter Quantity: "))

    books.append({
        "id": book_id,
        "title": title,
        "author": author,
        "genre": genre,
        "qty": qty
    })

    print("Book added successfully.")


def show_books():
    if not books:
        print("No books available.")
        return

    print("\n===== BOOK INVENTORY =====")

    for book in books:
        print(
            f"ID: {book['id']} | "
            f"Title: {book['title']} | "
            f"Author: {book['author']} | "
            f"Genre: {book['genre']} | "
            f"Qty: {book['qty']}"
        )


def search_book():
    keyword = input("Enter Book ID or Title: ").lower()

    found = False

    for book in books:
        if keyword == book["id"].lower() or keyword in book["title"].lower():
            print(book)
            found = True

    if not found:
        print("Book not found.")


def update_book():
    book_id = input("Enter Book ID to update: ")

    for book in books:
        if book["id"] == book_id:

            print("Leave blank to keep current value.")

            title = input(f"Title ({book['title']}): ")
            author = input(f"Author ({book['author']}): ")
            genre = input(f"Genre ({book['genre']}): ")
            qty = input(f"Quantity ({book['qty']}): ")

            if title:
                book["title"] = title

            if author:
                book["author"] = author

            if genre:
                book["genre"] = genre

            if qty:
                book["qty"] = int(qty)

            print("Book updated successfully.")
            return

    print("Book not found.")


def delete_book():
    book_id = input("Enter Book ID to delete: ")

    for book in books:
        if book["id"] == book_id:
            books.remove(book)
            print("Book deleted successfully.")
            return

    print("Book not found.")


# ==========================
# ISSUE / RETURN
# ==========================

def issue_book():
    book_id = input("Enter Book ID: ")
    student = input("Enter Student Name: ")

    for book in books:

        if book["id"] == book_id:

            if book["qty"] <= 0:
                print("Book not available.")
                return

            book["qty"] -= 1

            issued_books.append({
                "student": student,
                "book_id": book_id,
                "title": book["title"]
            })

            print("Book issued successfully.")
            return

    print("Book not found.")


def return_book():
    student = input("Enter Student Name: ")
    book_id = input("Enter Book ID: ")

    for issue in issued_books:

        if issue["student"] == student and issue["book_id"] == book_id:

            issued_books.remove(issue)

            for book in books:
                if book["id"] == book_id:
                    book["qty"] += 1
                    break

            print("Book returned successfully.")
            return

    print("Issue record not found.")


# ==========================
# OTHER FEATURES
# ==========================

def check_availability():
    book_id = input("Enter Book ID: ")

    for book in books:
        if book["id"] == book_id:
            print(f"Available Copies: {book['qty']}")
            return

    print("Book not found.")


def view_issued_books():

    if not issued_books:
        print("No books currently issued.")
        return

    print("\n===== ISSUED BOOKS =====")

    for issue in issued_books:
        print(
            f"Student: {issue['student']} | "
            f"Book ID: {issue['book_id']} | "
            f"Title: {issue['title']}"
        )


def count_books():

    total_titles = len(books)
    total_copies = sum(book["qty"] for book in books)

    print(f"Total Different Books: {total_titles}")
    print(f"Total Available Copies: {total_copies}")


# ==========================
# MENU
# ==========================

def menu():

    load_data()

    while True:

        print("\n")
        print("===== LIBRARY MANAGEMENT SYSTEM =====")
        print("1. Add Book")
        print("2. Show Books")
        print("3. Search Book")
        print("4. Update Book")
        print("5. Delete Book")
        print("6. Issue Book")
        print("7. Return Book")
        print("8. Check Availability")
        print("9. View Issued Books")
        print("10. Count Books")
        print("11. Save Data")
        print("12. Exit")

        choice = input("Enter Choice: ")

        if choice == "1":
            add_book()

        elif choice == "2":
            show_books()

        elif choice == "3":
            search_book()

        elif choice == "4":
            update_book()

        elif choice == "5":
            delete_book()

        elif choice == "6":
            issue_book()

        elif choice == "7":
            return_book()

        elif choice == "8":
            check_availability()

        elif choice == "9":
            view_issued_books()

        elif choice == "10":
            count_books()

        elif choice == "11":
            save_data()

        elif choice == "12":
            save_data()
            print("Exiting...")
            break

        else:
            print("Invalid choice.")


menu()