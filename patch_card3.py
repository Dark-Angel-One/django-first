import re

with open('todo_sql/templates/partials/note_card.html', 'r') as f:
    content = f.read()

# I am looking at the provided image. The user has added two notes, both empty except for the title "eee" and content "eee". But wait, in the image, the red note takes up half the screen. It seems like the bento-grid is stretching it vertically? Wait, the grid uses `grid-template-columns: repeat(auto-fill, minmax(240px, 1fr))`, and `align-items: start;`. But earlier I modified `style.css`! Let's check `style.css`.
