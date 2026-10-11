"""
LIBRARY MANAGEMENT SYSTEM (Basic Python - No OOP)
===================================================
This version uses only:
- Functions
- Lists / dictionaries
- Plain text file handling (open, read, write, append)

Data is stored in 3 simple text files:
- books.txt        -> each line: book_id,title,author,total_qty,available_qty
- members.txt      -> each line: member_id,name,email
- transactions.txt -> each line: txn_id,book_id,member_id,issue_date,due_date,return_date,status

Fields are separated by commas, and each record is one line.
"""

import os
from datetime import datetime, timedelta

# -----------------------------
# File names
# -----------------------------
BOOKS_FILE = "books.txt"
MEMBERS_FILE = "members.txt"
TRANSACTIONS_FILE = "transactions.txt"

FINE_PER_DAY = 5
LOAN_PERIOD_DAYS = 14


# -----------------------------
# Helper: make sure files exist
# -----------------------------
def ensure_files_exist():
    for filename in [BOOKS_FILE, MEMBERS_FILE, TRANSACTIONS_FILE]:
        if not os.path.exists(filename):
            open(filename, "w").close()   # create an empty file


# -----------------------------
# Helper: generate next ID
# by counting existing lines in a file
# -----------------------------
def get_next_id(filename, prefix_length=4):
    with open(filename, "r") as f:
        lines = f.readlines()
    return str(len(lines) + 1).zfill(prefix_length)


# =========================================================
# BOOK FUNCTIONS
# =========================================================
def add_book(title, author, quantity):
    book_id = get_next_id(BOOKS_FILE)
    # Append a new line to books.txt
    with open(BOOKS_FILE, "a") as f:
        f.write(f"{book_id},{title},{author},{quantity},{quantity}\n")
    print(f"Book added successfully. Book ID: {book_id}")


def view_all_books():
    with open(BOOKS_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        print("No books in the library yet.")
        return

    print("\n--- ALL BOOKS ---")
    for line in lines:
        book_id, title, author, qty, available = line.strip().split(",")
        print(f"[{book_id}] {title} by {author} | Available: {available}/{qty}")


def search_book(keyword):
    keyword = keyword.lower()
    with open(BOOKS_FILE, "r") as f:
        lines = f.readlines()

    found = False
    for line in lines:
        book_id, title, author, qty, available = line.strip().split(",")
        if keyword in title.lower() or keyword in author.lower():
            print(f"[{book_id}] {title} by {author} | Available: {available}/{qty}")
            found = True

    if not found:
        print("No matching books found.")


def remove_book(book_id):
    with open(BOOKS_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    removed = False
    for line in lines:
        current_id = line.strip().split(",")[0]
        if current_id == book_id:
            removed = True
            continue  # skip this line (i.e. delete it)
        new_lines.append(line)

    # Rewrite the whole file without the removed book
    with open(BOOKS_FILE, "w") as f:
        f.writelines(new_lines)

    if removed:
        print("Book removed successfully.")
    else:
        print("Book ID not found.")


# Used internally when issuing/returning books,
# to change the "available" count of one specific book.
def update_book_availability(book_id, change):
    with open(BOOKS_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        parts = line.strip().split(",")
        current_id, title, author, qty, available = parts
        if current_id == book_id:
            available = str(int(available) + change)
        new_lines.append(f"{current_id},{title},{author},{qty},{available}\n")

    with open(BOOKS_FILE, "w") as f:
        f.writelines(new_lines)


def get_book_by_id(book_id):
    with open(BOOKS_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split(",")
        if parts[0] == book_id:
            return parts   # [book_id, title, author, qty, available]
    return None


# =========================================================
# MEMBER FUNCTIONS
# =========================================================
def add_member(name, email):
    member_id = get_next_id(MEMBERS_FILE)
    with open(MEMBERS_FILE, "a") as f:
        f.write(f"{member_id},{name},{email}\n")
    print(f"Member registered successfully. Member ID: {member_id}")


def view_all_members():
    with open(MEMBERS_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        print("No members registered yet.")
        return

    print("\n--- ALL MEMBERS ---")
    for line in lines:
        member_id, name, email = line.strip().split(",")
        print(f"[{member_id}] {name} | {email}")


def get_member_by_id(member_id):
    with open(MEMBERS_FILE, "r") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split(",")
        if parts[0] == member_id:
            return parts
    return None


# =========================================================
# ISSUE / RETURN FUNCTIONS
# =========================================================
def issue_book(book_id, member_id):
    book = get_book_by_id(book_id)
    member = get_member_by_id(member_id)

    if book is None:
        print("Invalid Book ID.")
        return
    if member is None:
        print("Invalid Member ID.")
        return

    available = int(book[4])
    if available <= 0:
        print("No copies available right now.")
        return

    txn_id = get_next_id(TRANSACTIONS_FILE, prefix_length=5)
    issue_date = datetime.now().strftime("%Y-%m-%d")
    due_date = (datetime.now() + timedelta(days=LOAN_PERIOD_DAYS)).strftime("%Y-%m-%d")

    # status column: "issued" or "returned"
    with open(TRANSACTIONS_FILE, "a") as f:
        f.write(f"{txn_id},{book_id},{member_id},{issue_date},{due_date},NA,issued\n")

    update_book_availability(book_id, -1)
    print(f"Book issued successfully. Transaction ID: {txn_id} | Due date: {due_date}")


def return_book(txn_id):
    with open(TRANSACTIONS_FILE, "r") as f:
        lines = f.readlines()

    new_lines = []
    txn_found = False
    fine = 0

    for line in lines:
        parts = line.strip().split(",")
        current_txn_id, book_id, member_id, issue_date, due_date, return_date, status = parts

        if current_txn_id == txn_id:
            txn_found = True

            if status == "returned":
                print("This book has already been returned.")
                new_lines.append(line)
                continue

            today = datetime.now()
            due = datetime.strptime(due_date, "%Y-%m-%d")

            if today > due:
                overdue_days = (today - due).days
                fine = overdue_days * FINE_PER_DAY

            return_date = today.strftime("%Y-%m-%d")
            status = "returned"
            update_book_availability(book_id, +1)

        new_lines.append(f"{current_txn_id},{book_id},{member_id},{issue_date},{due_date},{return_date},{status}\n")

    with open(TRANSACTIONS_FILE, "w") as f:
        f.writelines(new_lines)

    if not txn_found:
        print("Invalid Transaction ID.")
    elif fine > 0:
        print(f"Book returned. Fine due: {fine}")
    else:
        print("Book returned successfully. No fine.")


def view_all_transactions():
    with open(TRANSACTIONS_FILE, "r") as f:
        lines = f.readlines()

    if not lines:
        print("No transactions yet.")
        return

    print("\n--- ALL TRANSACTIONS ---")
    for line in lines:
        txn_id, book_id, member_id, issue_date, due_date, return_date, status = line.strip().split(",")

        book = get_book_by_id(book_id)
        member = get_member_by_id(member_id)

        book_title = book[1] if book else "Unknown"
        member_name = member[1] if member else "Unknown"

        print(f"[{txn_id}] {book_title} -> {member_name} | Status: {status} | Due: {due_date}")


# =========================================================
# MAIN MENU
# =========================================================
def main():
    ensure_files_exist()

    menu = """
========== LIBRARY MANAGEMENT SYSTEM ==========
1.  Add Book
2.  Remove Book
3.  Search Book
4.  View All Books
5.  Register Member
6.  View All Members
7.  Issue Book
8.  Return Book
9.  View All Transactions
10. Exit
================================================
"""

    while True:
        print(menu)
        choice = input("Enter your choice (1-10): ").strip()

        if choice == "1":
            title = input("Book title: ").strip()
            author = input("Author: ").strip()
            try:
                quantity = int(input("Quantity: ").strip())
            except ValueError:
                print("Quantity must be a number.")
                continue
            add_book(title, author, quantity)

        elif choice == "2":
            book_id = input("Book ID to remove: ").strip()
            remove_book(book_id)

        elif choice == "3":
            keyword = input("Search by title/author: ").strip()
            search_book(keyword)

        elif choice == "4":
            view_all_books()

        elif choice == "5":
            name = input("Member name: ").strip()
            email = input("Member email: ").strip()
            add_member(name, email)

        elif choice == "6":
            view_all_members()

        elif choice == "7":
            book_id = input("Book ID: ").strip()
            member_id = input("Member ID: ").strip()
            issue_book(book_id, member_id)

        elif choice == "8":
            txn_id = input("Transaction ID: ").strip()
            return_book(txn_id)

        elif choice == "9":
            view_all_transactions()

        elif choice == "10":
            print("Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()