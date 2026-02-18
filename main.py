from fastmcp import FastMCP
import os
import aiosqlite

DB_PATH = os.path.join(os.path.dirname(__file__), 'expenses.db')
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), 'categories.json')

mcp = FastMCP("ExpenseTracker")

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                description TEXT DEFAULT ''
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS credits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                source TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS savings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                goal TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT DEFAULT ''
            )
        ''')
        await db.commit()

@mcp.tool()
async def add_expense(amount: float, category: str, date: str, subcategory: str = "", description: str = ""):
    """Add a new expense entry."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO expenses (amount, category, date, subcategory, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (amount, category, date, subcategory, description))
        await db.commit()
        return {"status": "success", "id": cursor.lastrowid}

@mcp.tool()
async def list_expenses(start_date: str, end_date: str):
    """List expenses entries within an inclusive date range (YYYY-MM-DD)."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT id, date, amount, category, subcategory, description FROM expenses
            WHERE date BETWEEN ? AND ?
            ORDER BY id ASC
        ''', (start_date, end_date)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

@mcp.tool()
async def edit_expense(id: int, amount=None, category=None, date=None, subcategory=None, description=None):
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
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, values)
        await db.commit()
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"Expense with id {id} not found"}
    return {"status": "success", "id": id, "updated_fields": len(updates)}

@mcp.tool()
async def delete_expense(id: int):
    """Delete an expense by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('DELETE FROM expenses WHERE id = ?', (id,))
        await db.commit()
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"Expense with id {id} not found"}
    return {"status": "success", "message": f"Expense {id} deleted"}

@mcp.tool()
async def add_credit(amount: float, source: str, date: str, description: str = ""):
    """Add a credit/income entry."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO credits (amount, source, date, description)
            VALUES (?, ?, ?, ?)
        ''', (amount, source, date, description))
        await db.commit()
        return {"status": "success", "id": cursor.lastrowid}

@mcp.tool()
async def list_credits():
    """List all credit/income entries."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT id, date, amount, source, description FROM credits ORDER BY id ASC') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

@mcp.tool()
async def edit_credit(id: int, amount=None, source=None, date=None, description=None):
    """Edit an existing credit by ID. Only provided fields will be updated."""
    updates = []
    values = []
    
    if amount is not None:
        updates.append("amount = ?")
        values.append(amount)
    if source is not None:
        updates.append("source = ?")
        values.append(source)
    if date is not None:
        updates.append("date = ?")
        values.append(date)
    if description is not None:
        updates.append("description = ?")
        values.append(description)
    
    if not updates:
        return {"status": "error", "message": "No fields to update"}
    
    values.append(id)
    query = f"UPDATE credits SET {', '.join(updates)} WHERE id = ?"
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, values)
        await db.commit()
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"Credit with id {id} not found"}
    return {"status": "success", "id": id, "updated_fields": len(updates)}

@mcp.tool()
async def delete_credit(id: int):
    """Delete a credit by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('DELETE FROM credits WHERE id = ?', (id,))
        await db.commit()
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"Credit with id {id} not found"}
    return {"status": "success", "message": f"Credit {id} deleted"}

@mcp.tool()
async def add_saving(amount: float, goal: str, date: str, description: str = ""):
    """Add a saving entry."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO savings (amount, goal, date, description)
            VALUES (?, ?, ?, ?)
        ''', (amount, goal, date, description))
        await db.commit()
        return {"status": "success", "id": cursor.lastrowid}

@mcp.tool()
async def list_savings():
    """List all saving entries."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT id, date, amount, goal, description FROM savings ORDER BY id ASC') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

@mcp.tool()
async def edit_saving(id: int, amount=None, goal=None, date=None, description=None):
    """Edit an existing saving by ID. Only provided fields will be updated."""
    updates = []
    values = []
    
    if amount is not None:
        updates.append("amount = ?")
        values.append(amount)
    if goal is not None:
        updates.append("goal = ?")
        values.append(goal)
    if date is not None:
        updates.append("date = ?")
        values.append(date)
    if description is not None:
        updates.append("description = ?")
        values.append(description)
    
    if not updates:
        return {"status": "error", "message": "No fields to update"}
    
    values.append(id)
    query = f"UPDATE savings SET {', '.join(updates)} WHERE id = ?"
    
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(query, values)
        await db.commit()
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"Saving with id {id} not found"}
    return {"status": "success", "id": id, "updated_fields": len(updates)}

@mcp.tool()
async def delete_saving(id: int):
    """Delete a saving by ID."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('DELETE FROM savings WHERE id = ?', (id,))
        await db.commit()
        if cursor.rowcount == 0:
            return {"status": "error", "message": f"Saving with id {id} not found"}
    return {"status": "success", "message": f"Saving {id} deleted"}

@mcp.tool()
async def get_summary():
    """Get a financial summary with total expenses, credits, and savings."""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT SUM(amount) FROM expenses')
        total_expenses = (await cursor.fetchone())[0] or 0
        
        cursor = await db.execute('SELECT SUM(amount) FROM credits')
        total_credits = (await cursor.fetchone())[0] or 0
        
        cursor = await db.execute('SELECT SUM(amount) FROM savings')
        total_savings = (await cursor.fetchone())[0] or 0
    
    balance = total_credits - total_expenses - total_savings
    
    return {
        "total_expenses": total_expenses,
        "total_credits": total_credits,
        "total_savings": total_savings,
        "balance": balance
    }

@mcp.resource("expense://categories", mime_type="application/json")
async def categories():
    """Read fresh each time so you can edit the file without restarting."""
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_db())
    mcp.run(transport="http", host="0.0.0.0", port=8000)