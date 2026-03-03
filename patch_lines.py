import re

# Patch note_card.html
with open('todo_sql/templates/partials/note_card.html', 'r') as f:
    content = f.read()

# Replace <p class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words max-h-60 overflow-hidden">{{ note.content|truncatechars:300 }}</p>
# with <div class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words line-clamp-[8]">{{ note.content|truncatechars:500 }}</div>
content = re.sub(
    r'<p class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words max-h-60 overflow-hidden">(.*?)</p>',
    r'<div class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words line-clamp-6 overflow-hidden max-h-48 relative">\1</div>',
    content
)
with open('todo_sql/templates/partials/note_card.html', 'w') as f:
    f.write(content)

# Patch app.js
with open('todo_sql/static/js/app.js', 'r') as f:
    app_js = f.read()

app_js = re.sub(
    r"const p = el\('p', 'text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words max-h-60 overflow-hidden'\);\s*p\.textContent = note\.content\.substring\(0, 300\);",
    r"const p = el('div', 'text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words line-clamp-6 overflow-hidden max-h-48 relative');\n        p.textContent = note.content.substring(0, 500);",
    app_js
)

with open('todo_sql/static/js/app.js', 'w') as f:
    f.write(app_js)
