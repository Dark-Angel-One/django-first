import re

# Wait, another problem in the image:
# The note-card has `min-h-[100px]`, but it has no `max-height` or fade effect for text, EXCEPT `max-h-60 overflow-hidden` on the `<p>`.
# BUT in the image, the `eee` is visible at the very bottom.
# Wait! Look at the image!
# The second "eee" is vertically aligned far away from the first "eee".
# Why would it be aligned so far?
# Because the `<p>` has `max-h-60`? No, if it has `max-h-60`, it's 240px. The space is 240px!
# Yes, the height is EXACTLY 240px + padding + title!
# But Google Keep collapses empty newlines!
# Google Keep doesn't let you just have a huge empty gap.
# Actually, wait. The problem is that the note-card uses `align-items: start;` in the grid.
# If there is another card in the SAME ROW that is very tall, the grid ROW becomes tall.
# AND because `.note-card` has `flex flex-col justify-between`, if the grid row is tall, does the card stretch to fill the cell?
# Yes! Wait, if `align-items: start;` is applied, the item DOES NOT stretch to fill the grid cell's height!
# BUT if the row is tall, and the item is NOT stretched...
# WAIT! Look at the image! The image only has ONE note.
# Why is ONE note so tall?
# Because the `<p>` element's content is `"eee\n\n\n\n\n\n\n\n\n\neee"`. It literally has many newlines.
# So the `<p>` expands to `max-h-60` (240px), taking up the space. The `overflow-hidden` clips the rest.
# The `eee` at the bottom is just the last visible line before the 240px limit!
# Is that a problem? The user sees a huge red block with two words.
# How to fix? Add `display: -webkit-box; -webkit-line-clamp: 8; -webkit-box-orient: vertical;`
# This truncates by lines instead of raw height!
# AND collapse multiple newlines! `note.content.replace(/\n{3,}/g, '\n\n')`
# YES! That's how Google Keep does it!
# Let's fix this in `note_card.html` and `app.js`!
