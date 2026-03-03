import re

with open('todo_sql/static/js/app.js', 'r') as f:
    js_content = f.read()

# I see it:
# `const card = el('div', 'note-card relative group rounded-lg border border-gray-200 dark:border-gray-700 p-4 transition-all hover:shadow-md cursor-default flex flex-col justify-between ${bgClass}');`

# The image shows two "eee" in one note: the title at the top, the content at the bottom!
# This is because the note-card has `justify-between` and there's a title at the top, and content below, BUT there is ALSO the hover actions!
# Actually, the hover actions `actionsDiv` are appended at the bottom.
# So `card.appendChild(contentDiv)` and then `card.appendChild(actionsDiv)`.
# If the note takes up the full page height, `justify-between` pushes `contentDiv` to the top and `actionsDiv` to the bottom!
# BUT WHY does the note take up the full page height?
# Because `bento-grid` has `align-items: start;`? No, if it only has one column, maybe it takes full height?
# Wait! In CSS Grid, if there's only 1 row, `align-items: start` should make it only as tall as its content.
# Wait, look at `index.html`:
# `<div class="bento-grid" id="other-notes">`
# Is there `grid-auto-rows: 1fr`? No.
# Could it be `min-h-[100px]` making it tall? No, 100px is small.
# Wait! In the image provided, there's ONE RED CARD taking up 1/3 width, but its HEIGHT is very tall! Almost a perfect rectangle like 400x600.
# Why is it so tall?
# Maybe `contentDiv` has `flex-1`?
# In `createNoteCardHTML`: `const contentDiv = el('div', 'cursor-pointer flex-1');`
# Ah! If `contentDiv` has `flex-1`, it will expand to fill available space in the `flex flex-col` parent.
# But why does the parent have so much available space?
# Oh, look at the image! `eee` is the Title and `eee` is the content.
# Wait! The title is at the very top. The content is at the very bottom.
# But if they are both in `contentDiv`, and `contentDiv` is `flex-1`, it would just be:
# `contentDiv` (title, body) -> taking up full space.
# But inside `contentDiv` they are just blocks. Why would `eee` body be pushed to the bottom of `contentDiv`?
# Because there are empty lines in the body!
# The user might have typed `eee\n\n\n\n\n\n\n\neee`.
# Yes! Look at the image: there is a huge empty space between the first "eee" and the second "eee".
# If the user pressed enter many times, the text is "eee\n\n\n\n\n\n\n\n\n\n\n\n\neee".
# And in `note_card.html`: `<p class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words max-h-60 overflow-hidden">{{ note.content|truncatechars:300 }}</p>`
# AND in `app.js`:
# ```
# const p = el('p', 'text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words max-h-60 overflow-hidden');
# p.textContent = note.content.substring(0, 300);
# ```
# The problem is `max-h-60` is Tailwind's max height, which is `240px` (`15rem`).
# Wait, if `max-h-60` is applied, how can the card be taller than 240px?
# Because Tailwind `max-h-60` might be 240px, but maybe the title and actions add more.
# BUT wait! If the user types a lot of newlines, shouldn't `max-h-60` hide the rest?
# YES! The `overflow-hidden` will hide the overflow.
# But what if the user types `eee\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\neee`?
# Then the note card becomes very tall and overflows?
# Wait! The image shows the first "eee" and the second "eee". The second "eee" is visible! If it was 30 newlines, maybe it's cut off?
# Actually, the user says "проблема с отображением" (problem with display) when there are empty lines. Google Keep usually limits the number of empty lines displayed, or truncates the height using a gradient fade-out (fade effect).
