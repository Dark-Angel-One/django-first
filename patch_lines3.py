import re

# Replace it in note_card.html to use line-clamp-8
with open('todo_sql/templates/partials/note_card.html', 'r') as f:
    content = f.read()

content = content.replace('line-clamp-6', 'line-clamp-8').replace('max-h-48', 'max-h-60')
with open('todo_sql/templates/partials/note_card.html', 'w') as f:
    f.write(content)

with open('todo_sql/static/js/app.js', 'r') as f:
    app_js = f.read()

app_js = app_js.replace('line-clamp-6', 'line-clamp-8').replace('max-h-48', 'max-h-60')
with open('todo_sql/static/js/app.js', 'w') as f:
    f.write(app_js)
