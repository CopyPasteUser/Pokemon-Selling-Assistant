import tkinter as tk
import json
import requests
import base64
from PIL import Image, ImageTk
import Pmw
from tkinter import messagebox
from io import BytesIO

# Function to fetch Pokemon names from the PokéAPI
def fetch_pokemon_names():
    response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=1010")
    if response.status_code == 200:
        data = response.json()
        for pokemon in data["results"]:
            pokemon_names.append(pokemon["name"])

# Function to fetch the sprite image of a Pokemon from the PokéAPI
def fetch_pokemon_sprite(pokemon_name):
    response = requests.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}")
    if response.status_code == 200:
        data = response.json()
        sprite_url = data["sprites"]["front_default"]
        response = requests.get(sprite_url)
        if response.status_code == 200:
            image_data = response.content
            return ImageTk.PhotoImage(Image.open(BytesIO(image_data)))
    return None

# Function to suggest Pokemon names based on user input
def suggest_pokemon(event):
    search_text = entry.get().lower()
    suggestions = [name for name in pokemon_names if search_text in name]
    name_menu.setlist(suggestions)

# Function to add the selected Pokemon to the purchase list
def add_pokemon_to_purchase():
    pokemon_name = name_menu.get()
    quantity = spinbox_quantity.get()

    if not pokemon_name:
        messagebox.showwarning("Error", "Please select a Pokemon.")
        return

    if not quantity:
        messagebox.showwarning("Error", "Please enter a quantity.")
        return

    purchase = {
        "Pokemon": pokemon_name,
        "Quantity": int(quantity),
        "Shiny": checkbox_var.get()
    }
    buyer_purchase.append(purchase)
    messagebox.showinfo("Success", f"{quantity} {pokemon_name.capitalize()} added to purchase.")

# Function to register the sale
def register_sale():
    username = entry_username.get().strip()
    if not username:
        messagebox.showwarning("Error", "Please enter a username.")
        return

    if not buyer_purchase:
        messagebox.showwarning("Error", "Please add at least one Pokemon to the purchase.")
        return

    buyer = None
    for existing_buyer in data:
        if existing_buyer["Username"] == username:
            buyer = existing_buyer
            break

    if buyer is None:
        buyer = {
            "Username": username,
            "Purchases": []
        }
        data.append(buyer)

    buyer["Purchases"].extend(buyer_purchase)
    buyer_purchase.clear()
    messagebox.showinfo("Success", "The sale has been successfully registered.")

    save_data()

    create_buyer_button(username)  # Refresh buyer button after registering the sale

# Function to create a button for the buyer
def create_buyer_button(username):
    button = tk.Button(buyer_buttons_frame, text=username, command=lambda: open_info_gui(username))
    button.pack(side=tk.LEFT)

# Function to open the buyer information GUI
def open_info_gui(username):
    for buyer in data:
        if buyer["Username"] == username:
            purchases = buyer["Purchases"]

            # Create a new GUI window or dialog
            info_window = tk.Toplevel()
            info_window.title("Buyer Information")

            # Create a frame to hold the purchased Pokemon details
            purchases_frame = tk.Frame(info_window)
            purchases_frame.pack()

            # Function to update the quantity in the data structure
            def update_quantity(purchase, new_quantity):
                purchase["Quantity"] = int(new_quantity)
                save_data()

            # Display the purchased Pokemon details
            for i, purchase in enumerate(purchases):
                pokemon_name = purchase["Pokemon"]
                quantity = purchase["Quantity"]
                shiny = purchase["Shiny"]

                # Create a label to display the Pokemon details
                pokemon_label = tk.Label(purchases_frame, text=f"{pokemon_name.capitalize()}:")
                pokemon_label.grid(row=i, column=0, sticky=tk.W)

                # Create a Spinbox to edit the quantity
                quantity_spinbox = tk.Spinbox(purchases_frame, from_=0, to=99, width=2)
                quantity_spinbox.delete(0, tk.END)
                quantity_spinbox.insert(tk.END, quantity)
                quantity_spinbox.grid(row=i, column=1, padx=5, pady=5)

                # Create an Update button to save the new quantity
                update_button = tk.Button(
                    purchases_frame,
                    text="Update",
                    command=lambda p=purchase, q=quantity_spinbox: update_quantity(p, q.get())
                )
                update_button.grid(row=i, column=2)

                # Display shiny information
                if shiny:
                    shiny_label = tk.Label(purchases_frame, text="(Shiny)")
                    shiny_label.grid(row=i, column=3, sticky=tk.W)

            break

# Function to save data to the JSON file
def save_data():
    with open("sales_data.json", "w") as file:
        json.dump(data, file)

# Load data from the JSON file
try:
    with open("sales_data.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = []

pokemon_names = []
buyer_purchase = []  # Define buyer_purchase list

fetch_pokemon_names()

window = tk.Tk()
window.title("Pokemon Sales System")
window.geometry("600x300")
# Fetch Charizard sprite and convert it to a Tkinter-compatible image
charizard_sprite = fetch_pokemon_sprite("charizard")

# Set Charizard sprite as window icon
window.tk.call("wm", "iconphoto", window._w, charizard_sprite)

# Create a frame for the buyer buttons
buyer_buttons_frame = tk.Frame(window)
buyer_buttons_frame.pack()

# Create a label and entry for the username
label_username = tk.Label(window, text="Username:")
label_username.pack()
entry_username = tk.Entry(window)
entry_username.pack()

# Create a label and entry for searching Pokemon
label_search = tk.Label(window, text="Search Pokemon:")
label_search.pack()
entry = tk.Entry(window)
entry.pack()

# Create a dropdown menu for selecting Pokemon names
name_menu = Pmw.ComboBox(window, dropdown=1, scrolledlist_items=pokemon_names, listheight=150)
name_menu.pack()
entry.bind("<KeyRelease>", suggest_pokemon)

# Create a spinbox for selecting the quantity of the purchased Pokemon
label_quantity = tk.Label(window, text="Quantity:")
label_quantity.pack()
spinbox_quantity = tk.Spinbox(window, from_=0, to=99, width=2)
spinbox_quantity.pack()

# Create a checkbox for selecting if the Pokemon is shiny
checkbox_var = tk.BooleanVar()
checkbox_shiny = tk.Checkbutton(window, text="Shiny", variable=checkbox_var)
checkbox_shiny.pack()

# Create a button to add the selected Pokemon to the purchase list
button_add = tk.Button(window, text="Add to Purchase", command=add_pokemon_to_purchase)
button_add.pack()

# Create a label to display the purchased Pokemon
label_purchases = tk.Label(window, text="Purchases:")
label_purchases.pack()

# Create a button to register the sale
button_register = tk.Button(window, text="Register Sale", command=register_sale)
button_register.pack()

# Function to delete a customer
def delete_customer(username):
    for buyer in data:
        if buyer["Username"] == username:
            data.remove(buyer)
            save_data()
            messagebox.showinfo("Success", f"{username} has been deleted.")
            break

    # Clear the buyer buttons frame and recreate buyer buttons after deletion
    for widget in buyer_buttons_frame.winfo_children():
        widget.destroy()

    for buyer in data:
        create_buyer_button(buyer["Username"])

# Create a label to display the purchased Pokemon
label_purchases = tk.Label(window, text="Purchases:")
label_purchases.pack()

# Function to create a button for the buyer
def create_buyer_button(username):
    button = tk.Button(buyer_buttons_frame, text=username, command=lambda: open_info_gui(username))
    button.pack(side=tk.LEFT)

    # Add a delete button for the buyer
    delete_button = tk.Button(buyer_buttons_frame, text="x", command=lambda u=username: delete_customer(u))
    delete_button.pack(side=tk.LEFT)

# Load and display the buyer information GUI for existing buyers
for buyer in data:
    username = buyer["Username"]
    create_buyer_button(username)

window.mainloop()
