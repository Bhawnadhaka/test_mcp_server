from fastmcp import FastMCP
import os
import sqlite3

DB_PATH= os.path.join(os.path.dirname(__file__), 'expenses.db')

CATEGORIES_PATH=os.path.join(os.path.dirname(__file__), 'categories.json')
mcp=FastMCP("ExpenseTracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                description TEXT DEFAULT ''
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                source TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS savings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                goal TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
        ''')

init_db()

@mcp.tool()
def add_expense(amount, category, date, subcategory = "", description= ""):
    with sqlite3.connect(DB_PATH) as c:
        cur=c.execute('''
            INSERT INTO expenses (amount, category, date, subcategory, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (amount, category, date, subcategory, description))
    return {"status": "success","id":cur.lastrowid}

@mcp.tool()
def list_expenses(start_date,end_date):
    "list expenses entries within an inclusive date range (YYYY-MM-DD)"
    with sqlite3.connect(DB_PATH) as c:
        cur=c.execute('''
            SELECT id,date,amount,category,subcategory,description FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
        ''', (start_date,end_date) )
        cols=[d[0] for d in cur.description]
    return [dict(zip(cols,r)) for r in cur.fetchall()]

@mcp.tool()
def edit_expense(id: int, amount=None, category=None, date=None, subcategory=None, description=None):
    """Edit an existing expense by ID. Only provided fields will be updated."""
    updates = []
    values = []
    
    if amount is not None:
        updates.append("amount = ?")
        values.append(amount)
    if category is not None:
        updates.append("category = ?")
        values.append(category)
    if date is not None:
        updates.append("date = ?")
        values.append(date)
    if subcategory is not None:
        updates.append("subcategory = ?")
        values.append(subcategory)
    if description is not None:
        updates.append("description = ?")
        values.append(description)
    
    if not updates:
        return {"status": "error", "message": "No fields to update"}
    
    values.append(id)
    query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?"
    
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(query, values)
        if cur.rowcount == 0:
            return {"status": "error", "message": f"Expense with id {id} not found"}
    return {"status": "success", "id": id, "updated_fields": len(updates)}

@mcp.tool()
def delete_expense(id: int):
    """Delete an expense by ID."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute('DELETE FROM expenses WHERE id = ?', (id,))
        if cur.rowcount == 0:
            return {"status": "error", "message": f"Expense with id {id} not found"}
    return {"status": "success", "message": f"Expense {id} deleted"}

@mcp.tool()
def add_credit(amount: float, source: str, date: str, description: str = ""):
    """Add a credit/income entry."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute('''
            INSERT INTO credits (amount, source, date, description)
            VALUES (?, ?, ?, ?)
        ''', (amount, source, date, description))
    return {"status": "success", "id": cur.lastrowid}

@mcp.tool()
def list_credits():
    """List all credit/income entries."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute('SELECT id, date, amount, source, description FROM credits ORDER BY id ASC')
        cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool()
def add_saving(amount: float, goal: str, date: str, description: str = ""):
    """Add a saving entry."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute('''
            INSERT INTO savings (amount, goal, date, description)
            VALUES (?, ?, ?, ?)
        ''', (amount, goal, date, description))
    return {"status": "success", "id": cur.lastrowid}

@mcp.tool()
def list_savings():
    """List all saving entries."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute('SELECT id, date, amount, goal, description FROM savings ORDER BY id ASC')
        cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool()
def get_summary():
    """Get a financial summary with total expenses, credits, and savings."""
    with sqlite3.connect(DB_PATH) as c:
        total_expenses = c.execute('SELECT SUM(amount) FROM expenses').fetchone()[0] or 0
        total_credits = c.execute('SELECT SUM(amount) FROM credits').fetchone()[0] or 0
        total_savings = c.execute('SELECT SUM(amount) FROM savings').fetchone()[0] or 0
    
    balance = total_credits - total_expenses - total_savings
    
    return {
        "total_expenses": total_expenses,
        "total_credits": total_credits,
        "total_savings": total_savings,
        "balance": balance
    }

@mcp.resource("expense://categories",mime_type="application/json")
def categories():
    """Read fresh each time so you can edit the file without restarting"""
    with open(CATEGORIES_PATH,"r",encoding="utf-8") as f:
        return f.read()
        return f.read()

if __name__=="__main__":    
    mcp.run(transport="http",host="0.0.0.0",port=8000)