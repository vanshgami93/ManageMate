import streamlit as st
import sqlite3
import re
import pandas as pd

st.set_page_config(page_title="ManageMate", 
                   page_icon="fevicon.png", 
                   layout="centered", 
                   initial_sidebar_state="auto", 
                   menu_items=None)

def set_bg_hack_url():       
    st.markdown(
          f"""
          <style>
          .stApp {{
              background: url("https://raw.githubusercontent.com/vyasdhairya/cropapp/main/managemate2.png");
              background-size: cover
          }}
          </style>
          """,
          unsafe_allow_html=True
      )
set_bg_hack_url()

conn = sqlite3.connect('data1.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(Department TEXT,FirstName TEXT,LastName TEXT,Mobile TEXT,Email TEXT,password TEXT,Cpassword TEXT)')
def add_userdata(Department,FirstName,LastName,Mobile,Email,password,Cpassword):
    c.execute('INSERT INTO userstable(Department,FirstName,LastName,Mobile,Email,password,Cpassword) VALUES (?,?,?,?,?,?,?)',(Department,FirstName,LastName,Mobile,Email,password,Cpassword))
    conn.commit()
def login_user(Department,Email,password):
    c.execute('SELECT * FROM userstable WHERE Department =? AND Email =? AND password = ?',(Department,Email,password))
    data = c.fetchall()
    return data
def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data
def delete_user(Email):
    c.execute("DELETE FROM userstable WHERE Email="+"'"+Email+"'")
    conn.commit()
def create_producttable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable1(Product TEXT,Price TEXT)')
def add_productdata(Product,Price):
    c.execute('INSERT INTO userstable1(Product,Price) VALUES (?,?)',(Product,Price))
    conn.commit() 
def view_all_product():
	c.execute('SELECT * FROM userstable1')
	data = c.fetchall()
	return data
def delete_product(Product):
    c.execute("DELETE FROM userstable1 WHERE Product="+"'"+Product+"'")
    conn.commit()

from threading import Lock
# Create a lock to handle SQLite operations
sqlite_lock = Lock()
# Function to create the SQLite database and table if not exists
def create_table():
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Department TEXT,
                Name TEXT,
                email TEXT,
                product TEXT,
                quantity INTEGER,
                is_locked BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

# Function to insert or update the order in the database
def insert_order(Department,Name,email, product, quantity):
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        # Check if the order already exists
        cursor.execute('SELECT quantity FROM orders WHERE email = ? AND product = ?', (email, product))
        existing_quantity = cursor.fetchone()
        if existing_quantity is not None:
            # If the order exists, update the quantity
            new_quantity = existing_quantity[0] + quantity
            cursor.execute('UPDATE orders SET quantity = ? WHERE email = ? AND product = ?', (new_quantity, email, product))
        else:
            # If the order doesn't exist, insert a new row
            cursor.execute('INSERT INTO orders (Department,Name,email, product, quantity) VALUES (?, ?, ?, ?, ?)', (Department, Name, email, product, quantity))

# Function to retrieve all orders
def get_all_orders():
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT Department, Name, email, product, quantity,is_locked, timestamp FROM orders ORDER BY timestamp DESC')
        all_orders = cursor.fetchall()
    return all_orders

# Function to retrieve orders for a specific email
def get_orders_by_email(email):
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT Department, Name, email, product, quantity,is_locked, timestamp FROM orders WHERE email = ? ORDER BY timestamp DESC', (email,))
        orders_by_email = cursor.fetchall()
    return orders_by_email

# Function to select products and quantities
def select_products(products):
    selected_products = []
    quantities = []
    for product in products:
        quantity = st.number_input(f"Select quantity for {product}", min_value=-1000, max_value=1000, value=0)
        if quantity > -1000:
            selected_products.append(product)
            quantities.append(quantity)
    return selected_products, quantities
def select_products1(products):
    selected_products = []
    quantities = []
    for product in products:
        quantity = st.number_input(f"Select quantitys for {product}", min_value=-1000, max_value=1000, value=0)
        if quantity > -1000:
            selected_products.append(product)
            quantities.append(quantity)
    return selected_products, quantities

# Function to display all orders in DataFrame
def display_orders_dataframe(orders):
    if orders:
        df = pd.DataFrame(orders, columns=["Department", "Name", "Email", "Product", "Quantity", "is_locked","Timestamp"])
        df=df.drop(["is_locked"],axis=1)
        st.write("\n**Total Orders:**")
        st.dataframe(df, height=500, width=1000)
    else:
        st.write("No orders available.")
def does_table_exist(table_name):
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        return cursor.fetchone() is not None    
def reset_all_orders():
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET quantity = 0, is_locked = 0')
def are_all_quantities_zero(email):
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM orders WHERE email = ? AND quantity != 0', (email,))
        result = cursor.fetchone()
        return result[0] == 0 if result else False
def set_order_lock(email, lock_status):
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE orders SET is_locked = ? WHERE email = ?', (lock_status, email))        
def check_order_lock(email):
    with sqlite3.connect("orders.db") as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT is_locked FROM orders WHERE email = ?', (email,))
        result = cursor.fetchone()
        return result[0] if result else None
def does_table_item(table_name):
    with sqlite3.connect("data1.db") as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        return cursor.fetchone() is not None         

# Admin function to view and update orders
def admin_view_update_orders(product_list):
    if not does_table_exist("orders"):
        st.error("No orders")
    else:
        # Display all orders for admin
        all_orders = get_all_orders()
        df = pd.DataFrame(all_orders, columns=["Department", "Name", "Email", "Product", "Quantity","is_locked", "Timestamp"])
        df=df.drop(["is_locked"],axis=1)
        total_quantity_df = df.groupby("Product")["Quantity"].sum().reset_index()
        st.write("\n**Total Quantity of Products Order:**")
        st.dataframe(total_quantity_df, height=425, width=1000)
        ordd = pd.DataFrame(all_orders, columns=["Department", "Name", "Email", "Product", "Quantity", "is_locked","Timestamp"])
        ordd=ordd.drop(["is_locked"],axis=1)
        display_orders_dataframe(all_orders)
        email_to_update = st.text_input("Enter email to update orders:")
        orders_to_update = get_orders_by_email(email_to_update)
        display_orders_dataframe(orders_to_update)     
        selected_products, quantities = select_products1(product_list)
        if st.button("Update Orders"):
            with sqlite_lock:
                for product, quantity in zip(selected_products, quantities):
                    insert_order(ordd["Department"][0],ordd["Name"][0],email_to_update, product, quantity)
                st.success(f"Orders for {email_to_update} updated successfully!")
        if st.button("Reset All Orders"):
            reset_all_orders()
            st.success("All orders are ready to Deliver")


    
def main(Department,Name,user_email,product_list):
    if not does_table_exist("orders"):
        st.error("No orders")
        lock_status=0
    else:
        # Check if the order is locked
        lock_status = check_order_lock(user_email)
        
    if lock_status == 1:
        st.write(f"Order for {user_email} is locked.")
        # Display all orders in DataFrame
        orders_to_update = get_orders_by_email(user_email)
        display_orders_dataframe(orders_to_update)
    else:
        
        if are_all_quantities_zero(user_email):
            st.warning("Kindly Collect Products")
            
        st.subheader("Multiple Product Selection with Quantity")
        # Create the SQLite table if not exists
        create_table()
    
        # Display product selection and quantities
        selected_products, quantities = select_products(product_list)
    
        # Button to place the order
        if st.button("Place Order"):
            with sqlite_lock:
                for product, quantity in zip(selected_products, quantities):
                    insert_order(Department,Name,user_email, product, quantity)
                st.success(f"Order placed successfully for {user_email}!")
        # Display all orders in DataFrame
        orders_to_update = get_orders_by_email(user_email)
        display_orders_dataframe(orders_to_update)
        if st.button("Lock Order"):
            with sqlite_lock:
                # Update is_locked value to 1 when locking
                set_order_lock(user_email, 1)
                st.success(f"Order for {user_email} locked successfully!")

menu = ["Home","Login","SignUp"]
choice = st.sidebar.selectbox("Menu",menu)
if choice=="Home":
    print("")
    st.image('logo.png')
    
if choice=="Login":
    menu2 = ["HR","Admin","Production","Sales"]
    dept = st.sidebar.selectbox("Select Department",menu2)
    Email = st.sidebar.text_input("Email")
    Password = st.sidebar.text_input("Password",type="password")
    b1=st.sidebar.checkbox("Login")
    if b1:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, Email):    
            result = login_user(dept,Email,Password)
            dd=pd.DataFrame(result,columns=["Department","FirstName","LastName","Mobile","Email","password","Cpassword"])
            if result:
                st.success("Logged In as {}".format(Email))
                if dept=="Admin":
                    menu3 = ["Add Product","Delete Product"]
                    ser = st.selectbox("Service",menu3)
                    if ser=="Add Product":
                        Product=st.text_input("Enter Product Name")
                        Price=st.text_input("Enter Product Price")
                        if st.button('Add'): 
                            create_producttable()
                            add_productdata(Product,Price)
                    if ser=="Delete Product":
                        Product=st.text_input("Enter Product Name")
                        if st.button('Delete'):
                            delete_product(Product)
                    if not does_table_item("userstable1"):
                        st.error("No items")
                    else:
                        product_result = view_all_product()
                        product_db = pd.DataFrame(product_result,columns=["Product","Price"])
                        st.dataframe(product_db,height=200, width=1000)    
                        admin_view_update_orders(product_db["Product"])
                else:
                    st.text("Product List")
                    create_producttable()
                    product_result = view_all_product()
                    product_db = pd.DataFrame(product_result,columns=["Product","Price"])
                    st.dataframe(product_db,height=200, width=1000)
                    main(dd["Department"][0],dd["FirstName"][0], Email,product_db["Product"])
            else:
                if dept=="Admin":
                    if Email=="a@a.com":
                        if Password=="12345":
                            Email1=st.text_input("Delete Email")
                            if st.button('Delete'):
                                delete_user(Email1)
                            user_result = view_all_users()
                            clean_db = pd.DataFrame(user_result,columns=["Department","FirstName","LastName","Mobile","Email","password","Cpassword"])
                            st.dataframe(clean_db)
                            
                        else:
                            st.warning("Incorrect Email/Password")
                    else:
                        st.warning("Incorrect Email/Password")
                    
                else:
                    st.warning("Incorrect Email/Password")
        else:
            st.warning("Not Valid Email")                            
    
if choice=="SignUp":
    menu2 = ["HR","Admin","Production","Sales"]
    dept = st.selectbox("Select Department",menu2)
    Fname = st.text_input("First Name")
    Lname = st.text_input("Last Name")
    Mname = st.text_input("Mobile Number")
    Email = st.text_input("Email")
    Password = st.text_input("Password",type="password")
    CPassword = st.text_input("Confirm Password",type="password")
    b2=st.button("SignUp")
    if b2:
        pattern=re.compile("(0|91)?[7-9][0-9]{9}")
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if Password==CPassword:
            if (pattern.match(Mname)):
                if re.fullmatch(regex, Email):
                    create_usertable()
                    add_userdata(dept,Fname,Lname,Mname,Email,Password,CPassword)
                    st.success("SignUp Success")
                    st.info("Go to Logic Section for Login")
                else:
                    st.warning("Not Valid Email")         
            else:
                st.warning("Not Valid Mobile Number")
        else:
            st.warning("Pass Does Not Match")
            