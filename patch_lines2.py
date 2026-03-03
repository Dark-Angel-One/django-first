import re

# Wait, `line-clamp-6` in Tailwind CSS applies `-webkit-line-clamp: 6; display: -webkit-box; -webkit-box-orient: vertical;`
# This fixes the height based on 6 lines, which is perfect!

# AND we need to collapse multiple newlines visually.
# `<div class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap break-words line-clamp-6 overflow-hidden max-h-48 relative">`
# Let's ensure it's written in `style.css` because some Tailwind versions don't have `line-clamp-X`.
