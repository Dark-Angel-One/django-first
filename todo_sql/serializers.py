from rest_framework import serializers
from .models import Note, Label, ChecklistItem

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name']

class ChecklistItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChecklistItem
        fields = ['id', 'text', 'is_checked', 'order']
        read_only_fields = ['id']

class NoteSerializer(serializers.ModelSerializer):
    checklist_items = ChecklistItemSerializer(many=True, required=False)
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Label.objects.all(), write_only=True, source='labels', required=False
    )

    class Meta:
        model = Note
        fields = [
            'id', 'title', 'content', 'color', 'is_pinned',
            'is_archived', 'is_trashed', 'is_checklist',
            'labels', 'label_ids', 'checklist_items', 'reminder_date',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        checklist_items_data = validated_data.pop('checklist_items', [])

        # labels are handled automatically by label_ids source due to ManyToMany
        # but we need to ensure label_ids are popped if handled manually?
        # No, DRF ModelSerializer handles ManyToMany if provided as PrimaryKeyRelatedField source
        # Wait, I used `source='labels'` for `label_ids`.
        # So `validated_data['labels']` will contain the Label objects.

        labels = validated_data.pop('labels', [])

        note = Note.objects.create(**validated_data)
        note.labels.set(labels)

        for item_data in checklist_items_data:
            ChecklistItem.objects.create(note=note, **item_data)

        return note

    def update(self, instance, validated_data):
        checklist_items_data = validated_data.pop('checklist_items', None)
        labels = validated_data.pop('labels', None)

        instance = super().update(instance, validated_data)

        if labels is not None:
             instance.labels.set(labels)

        if checklist_items_data is not None:
            # Smart update logic:
            # If ID is present, update. If not, create.
            # But the client might just send the whole list.
            # Let's check if the client sends IDs.
            # The current frontend implementation (Create) sends list without IDs.
            # Edit implementation... we don't have a full Edit form yet.
            # We need to support the "checklist toggling" feature requested.

            # For now, let's keep the clear-and-recreate strategy as it is robust for this scope
            instance.checklist_items.all().delete()
            for item_data in checklist_items_data:
                ChecklistItem.objects.create(note=instance, **item_data)

        return instance
