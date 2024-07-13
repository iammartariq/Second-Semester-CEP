# Modules used.
import os
from abc import ABC, abstractmethod
import datetime
import re
from colorama import Fore, Style, init

# Initialize colorama for colored terminal text
init(autoreset=True)


# Product class representing a product in the store
class Product:
    def __init__(self, product_id, name, price, description, quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.description = description
        self.quantity = quantity

# Method to decrease the quantity of the product
    def update_quantity(self, quantity):
        self.quantity -= quantity            

# Method to increase the quantity of the product
    def increase_quantity(self, quantity):
        self.quantity += quantity

# Method to display the product information
    def display_product_info(self):
        return f"{Fore.CYAN}Product ID: {self.product_id}, Name: {self.name}, Description: {self.description}, Price: {self.price}, Quantity: {self.quantity}{Style.RESET_ALL}"

# Method to compare two products by their ID (Operator overloading used)
    def __eq__(self, other):
        if isinstance(other, Product): 
            return self.product_id == other.product_id
        return False
    


# Abstract User class representing a user of the system
class User(ABC):
    def __init__(self, user_id, username, password, first_name, last_name, address):
        self.user_id = user_id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.shopping_history = []

# Abstract method for user login, to be implemented by subclasses
    @abstractmethod
    def login(self, username, password):
        pass

# Method to create a user account
    def create_account(self):
        pass

# Method to view shopping history of the user
    def view_shopping_history(self):
        for order in self.shopping_history:
            print(order.view_order_details())



# Customer class inheriting from User
class Customer(User):
    def __init__(self, user_id, username, password, first_name, last_name, address):
        super().__init__(user_id, username, password, first_name, last_name, address)
        self.cart = ShoppingCart(self)

# Method for customer login
    def login(self, username, password):
      while True:
        if self.username == username and self.password == password:
            print(Fore.GREEN + "Login successful!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Invalid credentials" + Style.RESET_ALL)
            username = input("Enter your username: ")
            password = input("Enter your password: ")



# Admin class inheriting from User
class Admin(User):
    def __init__(self, user_id, username, password, first_name, last_name, address):
        super().__init__(user_id, username, password, first_name, last_name, address)

# Method for admin login
    def login(self, username, password):
      while True:
        if self.username == username and self.password == password:
            print(Fore.GREEN + "Admin login successful!" + Style.RESET_ALL)
            break
        else:
            print(Fore.RED + "Invalid admin credentials" + Style.RESET_ALL)
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")

# Method to add a product to the store (that doesn't already exist) for users to purchase
    def add_product(self, store, product):
        store.products.append(product)

# Method to remove a product from the store by ID
    def remove_product(self, store, product_id):
        store.products = [product for product in store.products if product.product_id != product_id]

# Method to update product information
    def update_product_info(self, product, name=None, price=None, description=None, quantity=None):
        if name:
            product.name = name
        if price:
            product.price = price
        if description:
            product.description = description
        if quantity:
            product.quantity = quantity



# ShoppingCart class representing a shopping cart for a user
class ShoppingCart:
    def __init__(self, user):
        self.cart_id = id(self)
        self.user = user
        self.products = []
        self.total_price = 0.0

# Method to add a product to the cart
    def add_product(self, product, quantity=1):
        if quantity > product.quantity:
            print(Fore.RED + "Insufficient stock available" + Style.RESET_ALL)
            return
        product.update_quantity(quantity)
        self.products.append((product, quantity))
        self.total_price += product.price * quantity

# Method to remove a product from the cart
    def remove_product(self, product_id, quantity=None):
        found_product = False
        for i, (product, qty) in enumerate(self.products):
            if product.product_id == product_id:
                found_product = True
                if quantity is None or quantity >= qty:
                    self.total_price -= product.price * qty
                    product.increase_quantity(qty)
                    self.products.pop(i)
                    if quantity and quantity > qty:
                        print(Fore.YELLOW + f"You tried to remove {quantity}, but only {qty} were in the cart. All items removed." + Style.RESET_ALL)
                else:
                    self.total_price -= product.price * quantity
                    product.increase_quantity(quantity)
                    self.products[i] = (product, qty - quantity)
                break
        if not found_product:
            print(Fore.RED + "Product not found in cart" + Style.RESET_ALL)

# Method to view the cart contents
    def view_cart(self):
        for product, quantity in self.products:
            print(f"{product.display_product_info()}, Quantity you've added: {quantity}")
        print(f"{Fore.YELLOW}Total price: {self.total_price}{Style.RESET_ALL}")

# Method to checkout the cart and create an order
    def checkout(self):
        order = Order(self.user, self.products, self.total_price, datetime.datetime.now())
        self.user.shopping_history.append(order)
        self.products = []
        self.total_price = 0.0
        return order



# Order class representing an order made by a user
class Order:
    def __init__(self, user, products, total_price, date):
        self.order_id = id(self)
        self.user = user
        self.products = products
        self.total_price = total_price
        self.date = date

# Method to view order details
    def view_order_details(self):
        details = f"{Fore.MAGENTA}Order ID: {self.order_id}, Date: {self.date}{Style.RESET_ALL}\n"
        for product, quantity in self.products:
            details += f"{product.display_product_info()}, Quantity you've purchased: {quantity}\n"
        details += f"{Fore.YELLOW}Total price: {self.total_price}{Style.RESET_ALL}"
        return details



# Store class representing the online store
class Store:
    def __init__(self):
        self.products = []

    def display_all_products(self):
        for product in self.products:
            print(product.display_product_info())

    def search_product(self, name):
        for product in self.products:
            if product.name == name:
                return product
        return None




# UserDatabase class for managing user data
class UserDatabase:
    def __init__(self, filename):
        self.filename = filename
        self.users = self.load_users()

# Method to load users from a file
    def load_users(self):
        users = []
        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    user_data = eval(line.strip())
                    if user_data['type'] == 'Admin':
                        user = Admin(user_data['user_id'], user_data['username'], user_data['password'], user_data['first_name'], user_data['last_name'], user_data['address'])
                    else:
                        user = Customer(user_data['user_id'], user_data['username'], user_data['password'], user_data['first_name'], user_data['last_name'], user_data['address'])
                    users.append(user)
        except FileNotFoundError:
            pass
        return users

# Method to save users to a file
    def save_users(self):
        with open(self.filename, 'w') as file:
            for user in self.users:
                user_data = {
                    'type': 'Admin' if isinstance(user, Admin) else 'Customer',
                    'user_id': user.user_id,
                    'username': user.username,
                    'password': user.password,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'address': user.address
                }
                file.write(str(user_data) + '\n')

 # Method to add a user to the database
    def add_user(self, user):
        self.users.append(user)
        self.save_users()

# Method to check if a username already exists
    def username_exists(self, username):
        return any(user.username == username for user in self.users)


# Helper functions for user input and validation


# Function to check if the input is valid (not empty and does not contain digits)
def is_valid_input(value):
    return value.strip() and not any(char.isdigit() for char in value)

# Function to get valid input from the user
def get_valid_input(prompt):
    while True:
        value = input(prompt)
        if is_valid_input(value):
            return value
        else:
            print(Fore.RED + "Invalid input. Please enter a valid name." + Style.RESET_ALL)

# Function to make sure the user enters a valid password
def is_valid_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, ""

# Function to validate a username based on specific criteria
def is_valid_username(username):
    if len(username) < 8:
        return False, "Username must be at least 8 characters long."
    if not any(char.isalpha() for char in username):
        return False, "Username must contain at least one alphabet."
    if not re.search(r"[0-9]", username):
        return False, "Username must contain at least one number"
    return True, ""

# Function to clear the terminal screen for a cleaner output
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to prompt the user with a yes/no question and validate the response
def prompt_yes_no(message):
    while True:
        response = input(message).strip().lower()
        if response in ['yes', 'no']:
            return response == 'yes'
        else:
            print(Fore.RED + "Invalid input. Please enter 'yes' or 'no'." + Style.RESET_ALL)




# Main function to run the store application
def main():
    store = Store()
    user_db = UserDatabase('users.txt')

# Create an admin user (happens each time you run the code)
    admin = Admin(1, "admin1", "Admin@123", "Admin", "User", "123 Admin St")
    user_db.add_user(admin)

# List of products we've used (not the brightest of ideas) but its something :)
    products = [
        Product(1, "Laptop", 1000, "High performance laptop", 10),
        Product(2, "Smartphone", 500, "Latest model smartphone", 20),
        Product(3, "Tablet", 300, "High resolution tablet", 15),
        Product(4, "Headphones", 100, "Noise cancelling headphones", 25),
        Product(5, "Smartwatch", 200, "Feature rich smartwatch", 30),
        Product(6, "Camera", 800, "High resolution camera", 8),
        Product(7, "Printer", 150, "Wireless printer", 12),
        Product(8, "Monitor", 250, "4K monitor", 18),
        Product(9, "Keyboard", 50, "Mechanical keyboard", 40),
        Product(10, "Mouse", 30, "Wireless mouse", 50)
    ]

    for product in products:
        admin.add_product(store, product)

    

    while True:
        clear_terminal()
        print(Fore.BLUE + "WELCOME TO C-ZONE" + Style.RESET_ALL)
        print(Fore.BLUE + "ENJOY YOUR STAY HERE!" + Style.RESET_ALL)
        print("\nMain Menu:")
        print(Fore.CYAN + "1. Create Customer Account" + Style.RESET_ALL)
        print(Fore.CYAN + "2. Login as Customer" + Style.RESET_ALL)
        print(Fore.CYAN + "3. Login as Admin" + Style.RESET_ALL)
        print(Fore.CYAN + "4. View Store Products" + Style.RESET_ALL)
        print(Fore.CYAN + "5. Exit" + Style.RESET_ALL)
        choice = input("Enter your choice: ")


        if choice == '1':
            user_id = len(user_db.users) + 1

# Get and validate username
            while True:
                username = input("Enter username: ")
                if user_db.username_exists(username):
                    print(Fore.RED + "Username already exists. Please enter a different username." + Style.RESET_ALL)
                else:
                    valid_username, message = is_valid_username(username)
                    if valid_username:
                        break
                    else:
                        print(Fore.RED + message + Style.RESET_ALL)

            
# Get and validate password
            while True:
                password = input("Enter password: ")
                is_valid, message = is_valid_password(password)
                if is_valid:
                    break
                else:
                   print(Fore.RED + f"Invalid password: {message}" + Style.RESET_ALL)

# Gets other user details, the first name and last name have some restrictions but you can write anything for address as we think it doesn't matter too much for now.
            first_name = get_valid_input("Enter first name: ")
            last_name = get_valid_input("Enter last name: ")
            address = input("Enter address: ")

            customer = Customer(user_id, username, password, first_name, last_name, address)
            user_db.add_user(customer)
            print(Fore.GREEN + "Customer account created successfully" + Style.RESET_ALL)
            input("Press Enter to continue...")



        elif choice == '2':
            # Customer login process
            username = input("Enter username: ")
            password = input("Enter password: ")
            customer = next((u for u in user_db.users if isinstance(u, Customer) and u.username == username), None)
            if customer:
                customer.login(username, password)
                input("Press Enter to continue...")
            else:
                print(Fore.RED + "Customer not found" + Style.RESET_ALL)
                input("Press Enter to continue...")
                continue

            # Customer menu
            while True:
                clear_terminal()
                print("\nCustomer Menu:")
                print(Fore.YELLOW + "1. View Cart" + Style.RESET_ALL)
                print(Fore.YELLOW + "2. View Products" + Style.RESET_ALL)
                print(Fore.YELLOW + "3. Add Product to Cart" + Style.RESET_ALL)
                print(Fore.YELLOW + "4. Remove Product from Cart" + Style.RESET_ALL)
                print(Fore.YELLOW + "5. Checkout" + Style.RESET_ALL)
                print(Fore.YELLOW + "6. View Shopping History" + Style.RESET_ALL)
                print(Fore.YELLOW + "7. Logout" + Style.RESET_ALL)
                customer_choice = input("Enter your choice: ")


                if customer_choice == '1':
                    customer.cart.view_cart()
                    input("Press Enter to continue...")

                elif customer_choice == '2':
                    store.display_all_products()
                    input("Press Enter to continue...")

                elif customer_choice == '3':
                    while True:
                        store.display_all_products()
                        try:
                            product_id = int(input("Enter product ID to add: "))
                            quantity = int(input("Enter quantity: "))
                        except ValueError:
                            print(Fore.RED + "Invalid input. Please enter numeric values for product ID and quantity." + Style.RESET_ALL)
                            input("Press Enter to continue...")
                            continue
                        product = next((p for p in store.products if p.product_id == product_id), None)
                        if product:
                            customer.cart.add_product(product, quantity)
                        else:
                            print(Fore.RED + "Product not found" + Style.RESET_ALL)
                        if not prompt_yes_no("Do you want to add more products? (yes/no): "):
                            break
                    input("Press Enter to continue...")

                    
                elif customer_choice == '4':
                    while True:
                        customer.cart.view_cart()
                        try:
                            product_id = int(input("Enter product ID to remove: "))
                            quantity = int(input("Enter quantity to remove: "))
                        except ValueError:
                            print(Fore.RED + "Invalid input. Please enter numeric values for product ID and quantity." + Style.RESET_ALL)
                            input("Press Enter to continue...")
                            continue
                        customer.cart.remove_product(product_id, quantity)
                        if not prompt_yes_no("Do you want to remove more products? (yes/no): "):
                            break
                    input("Press Enter to continue...")


                elif customer_choice == '5':
                    order = customer.cart.checkout()
                    print(Fore.GREEN + "Order placed successfully" + Style.RESET_ALL)
                    print(order.view_order_details())
                    input("Press Enter to continue...")


                elif customer_choice == '6':
                    customer.view_shopping_history()
                    input("Press Enter to continue...")


                elif customer_choice == '7':
                    break
                else:
                    print(Fore.RED + "Invalid choice" + Style.RESET_ALL)
                    input("Press Enter to continue...")



        elif choice == '3':
            # Admin login process
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")
            admin = next((u for u in user_db.users if isinstance(u, Admin) and u.username == username), None)
            if admin:
                admin.login(username, password)
                input("Press Enter to continue...")
            else:
                print(Fore.RED + "Admin not found" + Style.RESET_ALL)
                input("Press Enter to continue...")
                continue

            # Admin menu
            while True:
                clear_terminal()
                print("\nAdmin Menu:")
                print(Fore.MAGENTA + "1. Add Product" + Style.RESET_ALL)
                print(Fore.MAGENTA + "2. Remove Product" + Style.RESET_ALL)
                print(Fore.MAGENTA + "3. Update Product Info" + Style.RESET_ALL)
                print(Fore.MAGENTA + "4. View All Products" + Style.RESET_ALL)
                print(Fore.MAGENTA + "5. Logout" + Style.RESET_ALL)
                admin_choice = input("Enter your choice: ")


                if admin_choice == '1':
                    product_id = len(store.products) + 1
                    name = input("Enter product name: ")
                    try:
                        price = float(input("Enter product price: "))
                        quantity = int(input("Enter product quantity: "))
                    except ValueError:
                        print(Fore.RED + "Invalid input. Please enter numeric values for price and quantity." + Style.RESET_ALL)
                        input("Press Enter to continue...")
                        continue
                    description = input("Enter product description: ")
                    product = Product(product_id, name, price, description, quantity)
                    admin.add_product(store, product)
                    print(Fore.GREEN + "Product added successfully" + Style.RESET_ALL)
                    input("Press Enter to continue...")


                elif admin_choice == '2':
                    store.display_all_products()
                    try:
                        product_id = int(input("Enter product ID to remove: "))
                    except ValueError:
                        print(Fore.RED + "Invalid input. Please enter a numeric value for product ID." + Style.RESET_ALL)
                        input("Press Enter to continue...")
                        continue
                    admin.remove_product(store, product_id)
                    print(Fore.GREEN + "Product removed successfully" + Style.RESET_ALL)
                    input("Press Enter to continue...")


                elif admin_choice == '3':
                    store.display_all_products()
                    try:
                        product_id = int(input("Enter product ID to update: "))
                    except ValueError:
                        print(Fore.RED + "Invalid input. Please enter a numeric value for product ID." + Style.RESET_ALL)
                        input("Press Enter to continue...")
                        continue
                    product = next((p for p in store.products if p.product_id == product_id), None)
                    if product:
                        name = input("Enter new name (leave blank to keep current): ")
                        price = input("Enter new price (leave blank to keep current): ")
                        description = input("Enter new description (leave blank to keep current): ")
                        quantity = input("Enter new quantity (leave blank to keep current): ")
                        try:
                            admin.update_product_info(product, name or None, float(price) if price else None, description or None, int(quantity) if quantity else None)
                            print(Fore.GREEN + "Product updated successfully" + Style.RESET_ALL)
                        except ValueError:
                            print(Fore.RED + "Invalid input. Please enter valid numeric values for price and quantity." + Style.RESET_ALL)
                    else:
                        print(Fore.RED + "Product not found" + Style.RESET_ALL)
                    input("Press Enter to continue...")


                elif admin_choice == '4':
                    store.display_all_products()
                    input("Press Enter to continue...")


                elif admin_choice == '5':
                    
                    break
                else:
                    print(Fore.RED + "Invalid choice" + Style.RESET_ALL)
                    input("Press Enter to continue...")


        elif choice == '4':
            # Display all products in the store
            store.display_all_products()
            input("Press Enter to continue...")


        elif choice == '5':
            # Exit the application
            break


        else:
            print(Fore.RED + "Invalid choice" + Style.RESET_ALL)
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
