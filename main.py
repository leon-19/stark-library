from mysql import connector
from prettytable import PrettyTable, from_db_cursor

conn = connector.connect(
    user='root',
    password='Buster',
    host='127.0.0.1',
    port=3306,
    auth_plugin='mysql_native_password',
    database="stark_library"
)


# Function to check if user exists.
def check_user(user_id):
    select_user_query = 'SELECT * FROM users WHERE id = %s'
    cursor = conn.cursor()
    cursor.execute(select_user_query, (user_id,))
    cursor.fetchall()
    cursor.close()
    if not cursor.rowcount > 0:
        print("Member not found!")
        return False
    return True


# Function to print all the books.
def print_all_books():
    books_query = "SELECT * FROM books"
    cursor = conn.cursor()
    cursor.execute(books_query)
    records = cursor.fetchall()
    cursor.close()

    table = PrettyTable(["ID", "Title", "Author", "Publisher", "Pages", "Price", "Copies"])
    table.align['Title'] = "l"
    table.align['Author'] = "l"
    table.align['Publisher'] = "l"

    for row in records:
        table.add_row([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])

    print(table)


# Function to add a new book to the database.
def add_new_book():
    title = input("ENTER BOOK TITLE: ")
    author = input("ENTER BOOK AUTHOR: ")
    publisher = input("ENTER BOOK PUBLISHER: ")
    pages = int(input("ENTER BOOK PAGES: "))
    price = int(input("ENTER BOOK PRICE: "))
    copies = int(input("ENTER BOOK COPIES: "))

    book_insert_query = 'INSERT INTO books (title, author, publisher, pages, price, copies) VALUES (%s, %s, %s, %s, %s, %s)'
    values = (title, author, publisher, pages, price, copies)

    cursor = conn.cursor()
    cursor.execute(book_insert_query, values)
    conn.commit()
    cursor.close()

    print("*** NEW BOOK ADDED SUCCESSFULLY ***")


# Function to add a new user to the database.
def add_new_user():
    member_name = input("ENTER MEMBER NAME: ")
    member_class = input("ENTER MEMBER CLASS: ")
    member_section = input("ENTER MEMBER SECTION: ")
    member_phone = int(input("ENTER PHONE NO.: "))
    member_email = input("ENTER YOUR EMAIL: ")

    user_insert_query = 'INSERT INTO users (name, class, section, phone, email) VALUES (%s, %s, %s, %s, %s)'
    values = (member_name, member_class, member_section, member_phone, member_email)

    cursor = conn.cursor()
    cursor.execute(user_insert_query, values)
    conn.commit()
    cursor.close()

    print("\n\n*** NEW MEMBER ADDED TO STARK LIBRARY ***\n\n")
    print("YOUR MEMBER ID IS:", cursor.lastrowid)


# Function to print all the members.
def print_all_users():
    books_query = "SELECT * FROM users"
    cursor = conn.cursor()
    cursor.execute(books_query)
    records = cursor.fetchall()
    cursor.close()

    table = PrettyTable(["ID", "Name", "Class", "Section", "Phone", "Email"])
    table.align['Name'] = "l"
    table.align['Phone'] = "l"
    table.align['Email'] = "l"

    for row in records:
        table.add_row([row[0], row[1], row[2], row[3], row[4], row[5]])

    print(table)


# Function to issue a book.
# Subtract one book from the database.
def issue_book():
    try:
        member_id = int(input("ENTER MEMBER ID: "))
        book_id = int(input("ENTER BOOK ID: "))
    except ValueError:
        print("Please enter a valid id")
        issue_book()
        return

        # Check member
    member_exists = check_user(member_id)
    if not member_exists:
        return

    select_book_query = 'SELECT * FROM books WHERE id = %s'
    cursor = conn.cursor()
    cursor.execute(select_book_query, (book_id,))

    if cursor.rowcount > 0:
        record = cursor.fetchall()

        if record[0][6] > 0:
            print("\nIssue", record[0][1], "by", record[0][2] + "?")
            print("1. Confirm\n")
            print("Or press any key to cancel...\n")

            if int(input()) == 1:
                # Issue the book
                issue_insert_query = 'INSERT INTO issued (user_id, book_id) VALUES (%s, %s)'
                update_book_query = 'UPDATE books SET copies = %s WHERE id = %s'
                issue_insert_values = (member_id, book_id)
                update_book_values = (int(record[0][6]) - 1, book_id)
                cursor = conn.cursor()
                cursor.execute(issue_insert_query, issue_insert_values)
                cursor.execute(update_book_query, update_book_values)
                conn.commit()
                cursor.close()
                print("\n*** BOOK ISSUED SUCCESSFULLY ***\n\n")
            else:
                print("\n*** ISSUE BOOK CANCELED ***\n\n")
                return
        else:
            print("\nBook not available")
            print("All", record[0][1], "books are issued")
    else:
        print("\nBook not found!")


# Function to return a book.
# Add the returned book to the database again.
def return_book():
    try:
        member_id = int(input("ENTER YOUR MEMBER ID: "))
    except ValueError:
        print("Please enter a valid id")
        return_book()
        return

        # Check member
    member_exists = check_user(member_id)
    if not member_exists:
        return

    issued_query = 'SELECT * FROM issued WHERE user_id = %s'
    cursor = conn.cursor()
    cursor.execute(issued_query, (member_id,))
    issued_record = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor()
    issued_books_query = 'SELECT * FROM books WHERE id = %s'
    for issued in issued_record:
        cursor.execute(issued_books_query, (issued[2],))

    if cursor.rowcount > 0:
        books_record = cursor.fetchall()

        table = PrettyTable(["ID", "Title", "Author", "Publisher", "Pages", "Price", "Copies"])
        table.align['Title'] = "l"
        table.align['Author'] = "l"
        table.align['Publisher'] = "l"

        for row in books_record:
            table.add_row([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])

        print("\n\nList of issued books:")
        print(table)

        book_id = int(input("ENTER BOOK ID OF THE BOOK: "))
        select_book_query = 'SELECT * FROM books WHERE id = %s'
        cursor = conn.cursor()
        cursor.execute(select_book_query, (book_id,))
        record = cursor.fetchall()

        print("\nReturn", record[0][1], "by", record[0][2] + "?")
        print("1. Confirm\n")
        print("Or press any key to cancel...\n")

        if int(input()):
            # Remove book from issued table.
            return_book_query = 'DELETE FROM issued WHERE book_id = %s AND user_id = %s'
            update_book_query = 'UPDATE books SET copies = %s WHERE id = %s'
            return_book_values = (book_id, member_id)
            update_book_values = (int(record[0][6]) + 1, book_id)
            cursor = conn.cursor()
            cursor.execute(return_book_query, return_book_values)
            cursor.execute(update_book_query, update_book_values)
            conn.commit()
            cursor.close()
            print("*** BOOK RETURNED SUCCESSFULLY ***")
        else:
            print("*** CANCELED BOOK RETURNED ***")
    else:
        print("No Books issued yet!")


# Main
def main():
    while True:
        print("*** LIBRARY MENU ***\n")
        print("1. SHOW ALL BOOKS")
        print("2. ADD BOOK")
        print("3. ADD NEW MEMBER")
        print("4. SHOW ALL MEMBERS")
        print("5. ISSUE BOOK")
        print("6. RETURN BOOK")
        print("7. EXIT\n")

        try:
            choice = int(input("\nENTER YOUR CHOICE : "))
        except ValueError:
            main()
            return

        if choice == 1:
            print_all_books()
            input("\nPress any key to go to menu")

        elif choice == 2:
            add_new_book()
            input("\nPress any key to go to menu")

        elif choice == 3:
            add_new_user()
            input("\nPress any key to go to menu")

        elif choice == 4:
            print_all_users()
            input("\nPress any key to go to menu")

        elif choice == 5:
            issue_book()
            input("\nPress any key to go to menu")

        elif choice == 6:
            return_book()
            input("\nPress any key to go to menu")

        elif choice == 7:
            print("***** THANKS FOR VISITING STARK LIBRARY ****")
            break

        else:
            print("Please choose a valid option")
            input("\nPress any key to go to menu")


# Greetings
print("*** WELCOME TO STARK LIBRARY ****\n\n")
# Start
main()
