import tkinter as tk
from tkinter import ttk
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATA_FILE = "finance_data.json"
MONTHLY_BUDGET = 2000


# ---------------- DATA ---------------- #

def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(transactions, f, indent=4)

transactions = load_data()

# ---------------- LOGIC ---------------- #

def add_transaction():
    try:
        amount = float(amount_entry.get())
        category = category_entry.get()
        t_type = type_var.get()

        if not category:
            status_label.config(text="Enter a category")
            return

        transactions.append({
            "amount": amount,
            "category": category,
            "type": t_type,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

        save_data()
        update_ui()

        amount_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)

    except ValueError:
        status_label.config(text="Enter a valid number")

def update_ui():
    listbox.delete(0, tk.END)

    income = 0
    expense = 0

    for t in transactions:
        sign = "+" if t["type"] == "Income" else "-"

        listbox.insert(
            tk.END,
            f"{t['date']} | {t['category']} | {sign}${t['amount']}"
        )

        if t["type"] == "Income":
            income += t["amount"]
        else:
            expense += t["amount"]

    balance = income - expense

    balance_label.config(
        text=f"Balance: ${balance:.2f}"
    )

    remaining = MONTHLY_BUDGET - expense

    budget_label.config(
        text=f"Budget Remaining: ${remaining:.2f}"
    )

    if MONTHLY_BUDGET > 0:
        percent_used = (expense / MONTHLY_BUDGET) * 100
    else:
        percent_used = 0

    budget_percent_label.config(
        text=f"Budget Used: {percent_used:.1f}%"
    )

    if remaining < 0:
        budget_label.config(fg="red")
    else:
        budget_label.config(fg="green")

    update_summary()
    update_charts()
# ---------------- SUMMARY ---------------- #

def update_summary():
    totals = {}

    income = 0
    expense = 0

    for t in transactions:
        cat = t["category"]

        if cat not in totals:
            totals[cat] = 0

        if t["type"] == "Income":
            income += t["amount"]
        else:
            expense += t["amount"]
            totals[cat] += t["amount"]

    summary_label.config(text=f"Income: ${income:.2f} | Expenses: ${expense:.2f}")

    category_box.delete(0, tk.END)
    for cat, total in totals.items():
        category_box.insert(tk.END, f"{cat}: ${total:.2f}")

# ---------------- CHARTS ---------------- #

def update_charts():
    for widget in chart_frame.winfo_children():
        widget.destroy()

    categories = {}
    income = 0
    expense = 0

    for t in transactions:
        if t["type"] == "Income":
            income += t["amount"]
        else:
            expense += t["amount"]
            cat = t["category"]
            categories[cat] = categories.get(cat, 0) + t["amount"]

    fig, axs = plt.subplots(1, 2, figsize=(7, 3))

    # PIE CHART
    if categories:
        axs[0].pie(categories.values(), labels=categories.keys(), autopct="%1.1f%%")
        axs[0].set_title("Expenses by Category")
    else:
        axs[0].text(0.5, 0.5, "No Data", ha="center")

    # BAR CHART
    axs[1].bar(
        ["Income", "Expenses"],
        [income, expense]
    )
    axs[1].set_ylabel("Amount ($)")
    axs[1].set_title("Income vs Expenses")

    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    plt.close(fig)


# ---------------- UI ---------------- #

root = tk.Tk()
root.title("Finance Dashboard Pro")
root.geometry("1000x600")

selected_month = tk.StringVar(value="All")

# LEFT PANEL (controls)
left = tk.Frame(root)
left.grid(row=0, column=0, sticky="n")

tk.Label(left, text="Amount").pack()
amount_entry = tk.Entry(left)
amount_entry.pack()

tk.Label(left, text="Category").pack()
category_entry = tk.Entry(left)
category_entry.pack()

type_var = tk.StringVar(value="Expense")
ttk.Combobox(left, textvariable=type_var, values=["Income", "Expense"]).pack()

tk.Button(left, text="Add Transaction", command=add_transaction).pack(pady=5)

status_label = tk.Label(left, text="")
status_label.pack()

# LIST
tk.Label(left, text="Filter Month").pack()

month_filter = ttk.Combobox(
    left,
    textvariable=selected_month,
    values=["All"]
)
month_filter.current(0)
month_filter.pack()
listbox = tk.Listbox(left, width=45)
listbox.pack(pady=10)

# SUMMARY
summary_label = tk.Label(left, text="Income: $0 | Expenses: $0")
summary_label.pack()

category_box = tk.Listbox(left, width=45)
category_box.pack(pady=5)

balance_label = tk.Label(left, text="Balance: $0.00", font=("Arial", 14))
balance_label.pack(pady=10)
budget_label = tk.Label(
    left,
    text=f"Budget Remaining: ${MONTHLY_BUDGET:.2f}",
    font=("Arial", 12, "bold")
)

budget_label.pack()
budget_percent_label = tk.Label(
    left,
    text="Budget Used: 0%"
)
budget_percent_label.pack()

# RIGHT PANEL (charts)
right = tk.Frame(root)
right.grid(row=0, column=1)

chart_frame = tk.Frame(right)
chart_frame.pack()

update_ui()

root.mainloop()