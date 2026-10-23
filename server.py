
from mcp.server.fastmcp import FastMCP
from datetime import datetime

mcp = FastMCP("CareLoop")

medicines = []

@mcp.tool()
def add_medicine(name: str, reminder_time: str) -> str:
    """Add a medicine and its reminder time. Use 24-hour HH:MM format."""
    try:
        datetime.strptime(reminder_time, "%H:%M")
    except ValueError:
        return "Invalid time. Please use HH:MM format, for example 08:30."

    medicine = {
        "id": len(medicines) + 1,
        "name": name,
        "reminder_time": reminder_time,
        "status": "Pending"
    }
    medicines.append(medicine)
    return f"Added {name} at {reminder_time}. Status: Pending."

@mcp.tool()
def list_medicines() -> list:
    """List all medicines and their current dose statuses."""
    return medicines

@mcp.tool()
def update_dose(medicine_id: int, status: str) -> str:
    """Update dose status to Taken or Missed."""
    if status.lower() not in ["taken", "missed"]:
        return "Status must be Taken or Missed."

    for medicine in medicines:
        if medicine["id"] == medicine_id:
            medicine["status"] = status.title()
            return f"{medicine['name']} marked as {status.title()}."

    return "Medicine not found."

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
