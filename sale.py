import streamlit as st
import pandas as pd
import os
from fpdf import FPDF
from datetime import datetime

# --- File Setup ---
sales_file = "sales_data.csv"
expense_file = "expenses.csv"

if os.path.exists(sales_file):
    sales_df = pd.read_csv(sales_file)
else:
    sales_df = pd.DataFrame(columns=["Date", "Customer Name", "Item", "Quantity", "Price", "Total"])

if os.path.exists(expense_file):
    expense_df = pd.read_csv(expense_file)
else:
    expense_df = pd.DataFrame(columns=["Date", "Description", "Amount"])

# --- Admin Login System ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "customer_name" not in st.session_state:
    st.session_state.customer_name = ""
if "cart" not in st.session_state:
    st.session_state.cart = []

# Login
if not st.session_state.logged_in:
    st.title("Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials!")
else:
    # Logout Button
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    st.sidebar.markdown(f"### 📅 {datetime.now().strftime('%Y-%m-%d')}")
    # Sidebar Navigation
    st.sidebar.title("📂 Menu")
    option = st.sidebar.radio("Select Option", ["💰 Sales", "📊 Daily Sales", "📊 Total Sales", "💸 Expenses"])

    if option == "💰 Sales":
        st.title("khurram jewellers - Sale Page")

        # Show Subtotal at the top
        subtotal = sum(item["Total"] for item in st.session_state.cart)
        st.subheader(f"🛒 Cart Subtotal: {subtotal:.2f} PKR")

        # Customer Name Input
        if st.session_state.customer_name == "":
            st.session_state.customer_name = st.text_input("Enter Customer Name")
        st.write(f"**Customer:** {st.session_state.customer_name}")

        # Product Sale Section
        item_name = st.text_input("Product Name")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        price = st.number_input("Price per unit", min_value=0.0, format="%.2f")
        total_price = quantity * price
        st.write(f"Total Price: {total_price:.2f}")

        if st.button("+ Add to Cart"):
            st.session_state.cart.append({"Item": item_name, "Quantity": quantity, "Price": price, "Total": total_price})
            st.success(f"Added {item_name} to cart!")

        # Show Cart
        if st.session_state.cart:
            st.subheader("Cart Items")
            cart_df = pd.DataFrame(st.session_state.cart)
            st.table(cart_df)

        # Generate Sale Slip
        def generate_invoice(customer_name, cart_items):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 12)
            pdf.cell(200, 10, "Khurram Jeweller's", ln=True, align="C")
            pdf.set_font("Arial", size=10)
            pdf.cell(200, 10, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
            pdf.cell(200, 10, "-----------------------------", ln=True)
            pdf.cell(50, 10, "Item", border=1)
            pdf.cell(30, 10, "Qty", border=1)
            pdf.cell(40, 10, "Price", border=1)
            pdf.cell(40, 10, "Total", border=1)
            pdf.ln()

            grand_total = 0
            for item in cart_items:
                pdf.cell(50, 10, item["Item"], border=1)
                pdf.cell(30, 10, str(item["Quantity"]), border=1)
                pdf.cell(40, 10, f"{item['Price']:.2f}", border=1)
                pdf.cell(40, 10, f"{item['Total']:.2f}", border=1)
                pdf.ln()
                grand_total += item["Total"]

            pdf.cell(200, 10, "-----------------------------", ln=True)
            pdf.cell(200, 10, f"Total Amount: {grand_total:.2f} PKR", ln=True)

            pdf_file = f"invoice_{customer_name}.pdf"
            pdf.output(pdf_file)
            return pdf_file

        if st.button("Generate Sale Slip"):
            if st.session_state.cart:
                invoice_file = generate_invoice(st.session_state.customer_name, st.session_state.cart)
                new_sales = pd.DataFrame(st.session_state.cart)
                new_sales.insert(0, "Date", datetime.now().strftime('%Y-%m-%d'))
                new_sales.insert(1, "Customer Name", st.session_state.customer_name)
                sales_df = pd.concat([sales_df, new_sales], ignore_index=True)
                sales_df.to_csv(sales_file, index=False)
                st.session_state.cart = []
                st.session_state.customer_name = ""
                st.success("Sale completed! Invoice generated.")

                with open(invoice_file, "rb") as f:
                    st.download_button("Download Invoice", f, file_name=invoice_file, mime="application/pdf")

    elif option == "📊 Daily Sales":
        st.title("📊 Daily Sales Report")
        sales_df["Date"] = pd.to_datetime(sales_df["Date"]).dt.date
        today = datetime.now().date()
        daily_sales = sales_df[sales_df["Date"] == today]
        st.write(daily_sales)
        st.write(f"**Total Sales Today: {daily_sales['Total'].sum():.2f} PKR**")

    elif option == "📊 Total Sales":
        st.title("📊 Total Sales Report")
        st.write(sales_df)
        st.write(f"**Total Sales: {sales_df['Total'].sum():.2f} PKR**")

    elif option == "💸 Expenses":
        st.title("💸 Add Expenses")
        description = st.text_input("Expense Description")
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        if st.button("Add Expense"):
            new_expense = pd.DataFrame([[datetime.now().strftime('%Y-%m-%d'), description, amount]], columns=["Date", "Description", "Amount"])
            expense_df = pd.concat([expense_df, new_expense], ignore_index=True)
            expense_df.to_csv(expense_file, index=False)
            st.success("Expense added!")

        st.subheader("📄 Expense Report")
        st.write(expense_df)
        st.write(f"**Total Expenses: {expense_df['Amount'].sum():.2f} PKR**")
