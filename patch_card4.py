import re

with open('todo_sql/templates/partials/note_card.html', 'r') as f:
    content = f.read()

# I see a problem in the HTML snippet above.
# Actually let's look at index.html and how bento-grid is applied.
