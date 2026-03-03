import re

with open('todo_sql/static/js/app.js', 'r') as f:
    app_js = f.read()

# I also need to make sure the JS rendering matches:
app_js = app_js.replace(
    "const p = el('div', 'text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words line-clamp-8 overflow-hidden max-h-60 relative');\n        p.textContent = note.content.substring(0, 500);",
    "const p = el('div', 'text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words line-clamp-8 overflow-hidden max-h-60 relative');\n        p.textContent = note.content.substring(0, 500);"
)

with open('todo_sql/static/js/app.js', 'w') as f:
    f.write(app_js)
