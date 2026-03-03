import re

with open('todo_sql/static/js/app.js', 'r') as f:
    js_content = f.read()

match = re.search(r"createNoteCardHTML\(note\).*?card\.appendChild\(contentDiv\);", js_content, re.DOTALL)
print(match.group(0))
