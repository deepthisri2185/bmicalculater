import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

# --------------- Database Setup ---------------
conn = sqlite3.connect('bmi_users.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS bmi_data (
    username TEXT,
    date TEXT,
    weight REAL,
    height REAL,
    bmi REAL
)''')
conn.commit()

# --------------- BMI Calculation ---------------
def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def validate_inputs(username, weight, height):
    if not username:
        messagebox.showwarning("Input Error", "Enter a username.")
        return False
    try:
        weight = float(weight)
        height = float(height)
        if not (25 <= weight <= 300 and 0.9 <= height <= 2.5):
            raise ValueError
        return True
    except ValueError:
        messagebox.showerror("Input Error", "Weight [25-300kg], Height [0.9-2.5m].")
        return False

def calculate_bmi():
    username = username_e.get().strip()
    weight = weight_e.get()
    height = height_e.get()
    if not validate_inputs(username, weight, height):
        return
    weight = float(weight)
    height = float(height)
    bmi = round(weight / (height ** 2), 2)
    cat = bmi_category(bmi)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result_var.set(f"BMI: {bmi} ({cat})")
    cur.execute("INSERT INTO bmi_data VALUES (?,?,?,?,?)", (username, now, weight, height, bmi))
    conn.commit()

def show_history():
    username = username_e.get().strip()
    if not username:
        messagebox.showinfo("Info", "Enter the username to view history.")
        return
    cur.execute("SELECT date, weight, height, bmi FROM bmi_data WHERE username=? ORDER BY date", (username,))
    records = cur.fetchall()
    if not records:
        messagebox.showinfo("History", "No data found for this user!")
        return
    hist_win = tk.Toplevel(root)
    hist_win.title(f"BMI History: {username}")

    tree = ttk.Treeview(hist_win, columns=('date', 'weight', 'height', 'bmi'), show='headings')
    tree.heading('date', text='Date')
    tree.heading('weight', text='Weight (kg)')
    tree.heading('height', text='Height (m)')
    tree.heading('bmi', text='BMI')
    for rec in records:
        tree.insert('', 'end', values=rec)
    tree.pack(fill=tk.BOTH, expand=True)

def show_bmi_graph():
    username = username_e.get().strip()
    if not username:
        messagebox.showinfo("Info", "Enter username for graph.")
        return
    cur.execute("SELECT date, bmi FROM bmi_data WHERE username=? ORDER BY date", (username,))
    rows = cur.fetchall()
    if not rows:
        messagebox.showinfo("Graph", "No BMI history for this user.")
        return
    dates, bmis = zip(*rows)
    plt.figure(figsize=(8,4))
    plt.plot(dates, bmis, marker='o', label="BMI")
    plt.title(f"{username}'s BMI Trend")
    plt.xlabel('Date')
    plt.ylabel('BMI')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.legend()
    plt.show()

def reset_fields():
    username_e.delete(0, tk.END)
    weight_e.delete(0, tk.END)
    height_e.delete(0, tk.END)
    result_var.set("")

# --------------- GUI Setup ---------------
root = tk.Tk()
root.title("Advanced BMI Calculator")
root.geometry("420x320")

tk.Label(root, text="Username:").grid(row=0, column=0, sticky="e", padx=8, pady=6)
username_e = tk.Entry(root, width=25)
username_e.grid(row=0, column=1, padx=8, pady=6)

tk.Label(root, text="Weight (kg):").grid(row=1, column=0, sticky="e", padx=8, pady=6)
weight_e = tk.Entry(root, width=25)
weight_e.grid(row=1, column=1, padx=8, pady=6)

tk.Label(root, text="Height (m):").grid(row=2, column=0, sticky="e", padx=8, pady=6)
height_e = tk.Entry(root, width=25)
height_e.grid(row=2, column=1, padx=8, pady=6)

result_var = tk.StringVar()
tk.Label(root, textvariable=result_var, fg="blue", font=("Arial", 16)).grid(row=3, columnspan=2, pady=10)

tk.Button(root, text="Calculate BMI", command=calculate_bmi).grid(row=4, column=0, padx=8, pady=5)
tk.Button(root, text="Show History", command=show_history).grid(row=4, column=1, padx=8, pady=5, sticky="w")
tk.Button(root, text="BMI Trend Graph", command=show_bmi_graph).grid(row=5, column=0, padx=8, pady=5)
tk.Button(root, text="Reset", command=reset_fields).grid(row=5, column=1, padx=8, pady=5, sticky="w")

tk.Label(root, text="Weight: 25-300 kg | Height: 0.9-2.5 m", fg="gray").grid(row=6, columnspan=2)

root.mainloop()
