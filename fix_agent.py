import re

path = r'c:\projects\qtick-mcp-new\app\agent.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace "whatsAppText": whatsapp_text with "whatsAppText": whatsapp_text if whatsapp_text else response_text
# We do this for both occurrences
new_content = content.replace('"whatsAppText": whatsapp_text', '"whatsAppText": whatsapp_text if whatsapp_text else response_text')

with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Replacement complete.")
