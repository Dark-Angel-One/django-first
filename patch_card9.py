import re

# Another thing about masonry grid!
# The bento-grid class is just a grid layout! CSS Grid doesn't natively support masonry layouts!
# `grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));`
# `gap: 16px;`
# `align-items: start;`
# This places items in rows. If one item in a row is tall, the WHOLE ROW takes that height!
# YES! That's exactly how CSS Grid works. If there's a tall item next to a short item, the short item's row cell is tall, but since it has `align-items: start`, the short item doesn't stretch.
# BUT wait, does the short item stretch?
# The image shows ONLY ONE ITEM. So we can't see the row effect.
# Oh, wait! Look at the image carefully.
# The card has `eee` at the top and `eee` at the bottom. The space between them is RED. The rest of the page is dark gray.
# The card looks exactly like a tall rectangle.
# Maybe the issue is actually that it's taking up so much space, OR maybe the text is cut off without any visual indication?
# Wait! Google Keep uses Masonry layout! CSS Grid can't do true Masonry (varying row heights) without `grid-template-rows: masonry` (which is experimental).
# The current app uses `bento-grid`. To fix the display problem (masonry), we can use columns!
# `column-count: 1; @media(min-width: 600px) { column-count: 2; } ...`
# Wait, SortableJS doesn't work well with CSS multi-columns because items jump between columns unpredictably.
# Let's see what the user explicitly requested: "проблема с отображением" (problem with display) -> I need to fix it.
