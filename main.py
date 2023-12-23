import pymongo
from faker import Faker
from datetime import date
import csv

fake = Faker()
client = pymongo.MongoClient('mongodb+srv://igor:1234@cluster0.pxmtxbe.mongodb.net/')
db = client['coffee_shop']
customers_collection = db['customers']
orders_collection = db['orders']
employees_collection = db['employees']

# faker
# for _ in range(100):
#     customers_collection.insert_one({
#         'customer_id': _,
#         'name': fake.name(),
#         'address': fake.address(),
#         'phone_number': fake.phone_number()
#     })

def login(username, password):
    employees = employees_collection.find()
    for employee in employees:
        if employee['username'] == username and employee['password'] == password:
            return employee['role']

def clerk_menu():
    while True:
        print("\nMenu for Clerks:")
        print("1. Add order")
        print("2. Add order (new customer)")
        print("3. Assign order to delivery")
        print("4. View pending orders")
        print("5. Exit")
        choice = input("Select the number: ")
        if choice == '1':
            customer_id = int(input("Enter customer ID: "))
            description = input("Enter order description: ")
            total_amount = int(input("Enter amount: "))
            clerk_id = int(input("Enter your clerk ID: "))
            add_order(customer_id, description, total_amount, clerk_id)
            print("\nOrder was added successfully!")
        elif choice == '2':
            name = input("Enter customer name: ")
            address = input("Enter customer address: ")
            phone_number = input("Enter customer phone number: ")
            customer_id = add_new_customer(name, address, phone_number)
            description = input("Enter order description: ")
            total_amount = int(input("Enter amount: "))
            clerk_id = int(input("Enter your clerk ID: "))
            add_order(customer_id, description, total_amount, clerk_id)
            print("\nOrder was added successfully!")
        elif choice == '3':
            order_id = int(input("Enter order ID: "))
            delivery_employee_id = int(input("Enter delivery employee ID: "))
            assign_order(order_id, delivery_employee_id)
            print("\nOrder was successfully assigned to delivery!")
        elif choice == '4':
            view_pending_orders()
        elif choice == '5':
            break
        else:
            print("Wrong choice!")

def add_order(customer_id, description, total_amount, clerk_id):
    last_order = orders_collection.find_one(sort=[("order_id", pymongo.DESCENDING)])
    last_order_id = last_order['order_id'] if last_order else 0  

    order_data = {
        'order_id': str(int(last_order_id) + 1),  
        'description': description,
        'order_date': date.today().isoformat(),
        'total_amount': total_amount,
        'clerk_id': clerk_id,
        'customer_id': customer_id,
        'completed': False
    }
    orders_collection.insert_one(order_data)



def view_pending_orders():
    orders = orders_collection.find({'completed': False})
    if not orders:
        print("\nNo pending orders.")
    else:
        print("\nPending Orders:")
        for order in orders:
            print(f"Order ID: {order['order_id']}, Description: {order['description']}, Amount: {order['total_amount']}")

def add_new_customer(name, address, phone_number):
    last_customer = customers_collection.find_one(sort=[("customer_id", pymongo.DESCENDING)])
    last_customer_id = last_customer['customer_id'] if last_customer else 0  

    customer_data = {
        'customer_id': str(int(last_customer_id) + 1),  
        'name': name,
        'address': address,
        'phone_number': phone_number
    }
    customers_collection.insert_one(customer_data)
    return customer_data['customer_id']


def assign_order(order_id, delivery_employee_id):
    clerk_id = int(input("Enter your clerk ID: "))
    orders_collection.update_one({'order_id': order_id}, {'$set': {'clerk_id': clerk_id}})
    
def delivery_menu():
    while True:
        print("\nMenu for Delivery:")
        print("1. Mark order as completed")
        print("2. Your pending deliveries")
        print("3. Exit")

        choice = input("Select the number: ")

        if choice == '1':
            order_id = int(input("Enter order ID: "))
            complete_order(order_id)
            print("\nOrder was completed successfully!")
        elif choice == '2':
            view_pending_orders()
        elif choice == '3':
            break
        else:
            print("\nWrong choice!")

def complete_order(order_id):
    orders_collection.update_one({'order_id': str(order_id)}, {'$set': {'completed': True}})


def manager_menu():
    while True:
        print("\nMenu for Managers:")
        print("1. Customer profile")
        print("2. Orders on day")
        print("3. Orders set by clerk")
        print("4. Pending orders")
        print("5. View Customers (exports to csv)")
        print("6. View Employees (exports to csv)")
        print("7. View Orders (exports to csv)")
        print("8. Export Orders to CSV")
        print("9. Exit")

        choice = input("Select the number: ")

        if choice == '1':
            customer_profile()
        elif choice == '2':
            orders_on_day()
        elif choice == '3':
            orders_set_by_clerk()
        elif choice == '4':
            view_pending_orders()
        elif choice == '5':
            export_customers_csv()
        elif choice == '6':
            export_employees_csv()
        elif choice == '7':
            export_orders_csv()
        elif choice == '8':
            specific_order_csv()
        elif choice == '9':
            break
        else:
            print("\nWrong choice!")

def export_customers_csv():
    customers = customers_collection.find()
    with open('customers.csv', 'w', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=list(customers[0].keys()))
        csv_writer.writeheader()
        for customer in customers:
            csv_writer.writerow(customer)

def customer_profile():
    customer_id = int(input("Enter customer ID: "))

    customer = customers_collection.find_one({'customer_id': customer_id})
    cursor = orders_collection.find({'customer_id': customer_id})

    if not customer:
        print("\nCustomer does not exist.")
    else:
        print("\nCustomer Profile:")
        print(f"Customer ID: {customer['customer_id']} Customer Name: ", customer['name'])
        print(f"Address: {customer['address']} Phone Number: {customer['phone_number']}")

        cursor = orders_collection.find({'customer_id': customer_id})
        if cursor:
            print("\nOrders:")
            for order in cursor:
                print(f"\nOrder ID: {order['order_id']},\nDescription: {order['description']},\nAmount: {order['total_amount']}")

def orders_on_day():
    order_date = input("Enter date (YYYY-MM-DD): ")
    orders = orders_collection.find({'order_date': order_date})

    if not orders:
        print("\nNo orders on this date.")
    else:
        print("\nOrders on", order_date)
        for order in orders:
            print(f"\nOrder ID: {order['order_id']},\nDescription: {order['description']},\nAmount: {order['total_amount']}")

def orders_set_by_clerk():
    clerk_id = int(input("Enter clerk ID: "))
    orders = orders_collection.find({'clerk_id': clerk_id})

    if not orders:
        print("\nNo orders were set by this clerk.")
    else:
        print("\nOrders set by this clerk:")
        for order in orders:
            print(f"\nOrder ID: {order['order_id']},\nDescription: {order['description']},\nAmount: {order['total_amount']}")

def export_employees_csv():
    employees = employees_collection.find()
    with open('employees.csv', 'w', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=list(employees[0].keys()))
        csv_writer.writeheader()
        for employee in employees:
            csv_writer.writerow(employee)

def export_orders_csv():
    orders = orders_collection.find()
    with open('orders.csv', 'w', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=list(orders[0].keys()))
        csv_writer.writeheader()
        for order in orders:
            csv_writer.writerow(order)

def specific_order_csv():
    order_id = input("Enter order ID: ")
    order = orders_collection.find_one({'order_id': order_id})
    with open(f'order_{order_id}.csv', 'w', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=list(order.keys()))
        csv_writer.writerow(order)

if __name__ == "__main__":
    while True:
        print("\nLogin Menu:")
        username = input("Username: ")
        password = input("Password: ")
        role = login(username, password)
        if role == 'clerk':
            clerk_menu()
        elif role == 'delivery':
            delivery_menu()
        elif role == 'manager':
            manager_menu()