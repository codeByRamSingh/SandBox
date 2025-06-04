import json
from datetime import datetime

# Initialize inventory 
inventory = {}

# Load inventory from file 
def load_inventory():
    try:
        with open("inventory.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save inventory to file (or later to HANA)
def save_inventory():
    with open("inventory.json", "w") as file:
        json.dump (inventory, file - (inventory, file, indent=4)

# Add a new product
def add_product(product_id, name, price, stock):
    inventory[product_id] = {"name": name, "price": price, "stock": stock}
    save_inventory()
    print(f"Added {name} to inventory.")

# Update stock after a sale or restock
def update_stock(product_id, quantity, is_sale=False):
    if product_id in inventory:
        if is_sale:
            if inventory[product_id]["stock"] >= quantity:
                inventory[product_id]["stock"] -= quantity
                print(f"Sold {quantity} units of {inventory[product_id]['name']}.")
            else:
                print("Not enough stock!")
        else:
            inventory[product_id]["stock"] += quantity
            print(f"Restocked {quantity} units of {inventory[product_id]['name']}.")
        save_inventory()
    else:
        print("Product not found!")

# Check for low stock
def check_low_stock(threshold=5):
    for product_id, details in inventory.items():
        if details["stock"] <= threshold:
            print(f"Low stock alert: {details['name']} has {details['stock']} units left.")

# Display all stocks
def display_all_stocks():
    if not inventory:
        print("Inventory is empty.")
    else:
        print("\nCurrent Inventory:")
        print("ID | Name | Price | Stock")
        print("-" * 30)
        for product_id, details in inventory.items():
            print(f"{product_id} | {details['name']} | {details['price']} | {details['stock']}")

# Main menu
def main():
    global inventory
    inventory = load_inventory()
    
    while True:
        print("\nInventory Management System")
        print("1. Add Product")
        print("2. Update Stock (Restock)")
        print("3. Record Sale")
        print("4. Check Low Stock")
        print("5. Display All Stocks")
        print("6. Exit")
        
        choice = input("Enter choice (1-6): ")
        
        if choice == "1":
            product_id = input("Enter product ID: ")
            name = input("Enter product name: ")
            try:
                price = float(input("Enter price: "))
                stock = int(input("Enter stock quantity: "))
                add_product(product_id, name, price, stock)
            except ValueError:
                print("Invalid input! Price and stock must be numeric.")
        
        elif choice == "2":
            product_id = input("Enter product ID: ")
            try:
                quantity = int(input("Enter quantity to restock: "))
                update_stock(product_id, quantity)
            except ValueError:
                print("Invalid input! Quantity must be numeric.")
        
        elif choice == "3":
            product_id = input("Enter product ID: ")
            try:
                quantity = int(input("Enter quantity sold: "))
                update_stock(product_id, quantity, is_sale=True)
            except ValueError:
                print("Invalid input! Quantity must be numeric.")
        
        elif choice == "4":
            check_low_stock()
        
        elif choice == "5":
            display_all_stocks()
        
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice! Try again.")

if __name__ == "__main__":
    main()