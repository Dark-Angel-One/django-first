import os
import django
import time
from django.db import connection
from django.contrib.auth.models import User

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from todo_sql.models import Note, ChecklistItem
from todo_sql.serializers import NoteSerializer

def benchmark_deletion(num_items_to_delete):
    # Setup
    user = User.objects.create_user(username=f'testuser_{int(time.time())}', password='password')
    note = Note.objects.create(user=user, title="Benchmark Note", is_checklist=True)

    # Create items
    items = [
        ChecklistItem(note=note, text=f"Item {i}", order=i)
        for i in range(num_items_to_delete)
    ]
    ChecklistItem.objects.bulk_create(items)

    # Prepare update data (empty checklist_items to delete all)
    data = {
        'checklist_items': []
    }

    serializer = NoteSerializer(instance=note, data=data, partial=True)
    if not serializer.is_valid():
        print(serializer.errors)
        return

    # Measure
    connection.queries_log.clear()
    start_time = time.time()

    serializer.save()

    end_time = time.time()
    num_queries = len(connection.queries)

    print(f"Deleted {num_items_to_delete} items.")
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Number of queries: {num_queries}")

    # Cleanup
    user.delete()

if __name__ == "__main__":
    benchmark_deletion(100)
