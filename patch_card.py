import re

with open('todo_sql/templates/partials/note_card.html', 'r') as f:
    content = f.read()

# I see what the issue is! The div structure of the card is messed up in the template!
# Wait, let's look at the template again.

with open('todo_sql/templates/partials/note_card.html', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:10]):
        print(f"{i}: {line.strip()}")
