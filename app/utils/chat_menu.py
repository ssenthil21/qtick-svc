
CHAT_MENU = {
    "1": "Get franchise summary for this month",
    "2": "List all offers",
    "3": "Get summary for today",
    "4": "Get weekly performance comparison",
    "5": "List all leads",
    "6": "List all appointments",
    "7": "I want to create an appointment. Guide me.",
    "8": "I want to create a new lead. Guide me."
}

def get_chat_menu_text():
    menu = "🔢 *Chat Shortcuts:*\n"
    menu += "1. 📊 Branch Summary (Month)\n"
    menu += "2. 🏷️ List Offers\n"
    menu += "3. 📉 Today's Summary\n"
    menu += "4. 📈 Performance Insight\n"
    menu += "5. 📋 Enquiries\n"
    menu += "6. 📅 Appointments\n"
    menu += "7. ➕ Create Appointment\n"
    menu += "8. ✍️ Create Lead\n\n"
    menu += "Type a number or ask normally!"
    return menu
