import re

with open('todo_sql/templates/partials/note_card.html', 'r') as f:
    content = f.read()

# I see a problem in the HTML snippet above. The "Labels" section inside the clickable area is actually OUTSIDE the main text but INSIDE `contentDiv`. The hover actions are OUTSIDE `contentDiv`.
# Wait, let's look at how the HTML elements are structured in note_card.html

content_to_replace = """        {% if note.labels.all %}
        <div class="flex flex-wrap gap-1 mt-2">
            {% for label in note.labels.all %}
            <span class="px-2 py-0.5 rounded-full bg-black/5 dark:bg-white/10 text-xs text-gray-700 dark:text-gray-300 cursor-pointer" onclick="event.stopPropagation(); window.location.href='/label/{{ label.name }}/'">{{ label.name }}</span>
            {% endfor %}
        </div>
        {% endif %}
    </div>

    <!-- Hover Actions -->
    <div class="flex justify-between items-center mt-4 opacity-0 group-hover:opacity-100 transition-opacity h-8">"""

if content_to_replace in content:
    print("Found it!")
else:
    print("Not found")
