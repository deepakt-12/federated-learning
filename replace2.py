import sys

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

start_idx = text.find('def health_dashboard_page():')
end_idx = text.find('def main():')

if start_idx == -1 or end_idx == -1:
    print(f"Error: start_idx={start_idx}, end_idx={end_idx}")
    sys.exit(1)

with open('new_code.py', 'r', encoding='utf-8') as f:
    new_func = f.read()

new_text = text[:start_idx] + new_func + '\n\n\n' + text[end_idx:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_text)

print("Successfully replaced successfully!")
