import os
import django
from django.db import connection
from django.test.utils import CaptureQueriesContext

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from todo_sql.models import Note, ChecklistItem

# Setup data
user, created = User.objects.get_or_create(username='testuser')
note = Note.objects.create(user=user, title='Test Note', is_checklist=True)
for i in range(10):
    ChecklistItem.objects.create(note=note, text=f'Item {i}', order=i)

# Baseline: Measure queries with prefetch_related
print("Measuring queries with prefetch_related...")
notes = Note.objects.filter(id=note.id).prefetch_related('checklist_items')

with CaptureQueriesContext(connection) as queries:
    for n in notes:
        items = n.preview_checklist_items
        print(f"Items found: {len(items)}")

print(f"Total queries: {len(queries)}")
for i, query in enumerate(queries):
    print(f"Query {i+1}: {query['sql']}")

if len(queries) > 2: # 1 for notes, 1 for prefetch, any extra is N+1
    print("N+1 detected!")
else:
    print("No N+1 detected (or only 1 note tested).")

# Cleanup
# Note.objects.filter(user=user).delete()
