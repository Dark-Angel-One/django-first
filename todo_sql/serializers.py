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
            'labels', 'label_ids', 'checklist_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        checklist_items_data = validated_data.pop('checklist_items', [])
        labels_data = validated_data.pop('labels', []) # handled by label_ids source

        # User should be passed in save() or context
        note = Note.objects.create(**validated_data)

        for item_data in checklist_items_data:
            ChecklistItem.objects.create(note=note, **item_data)

        return note

    def update(self, instance, validated_data):
        checklist_items_data = validated_data.pop('checklist_items', None)
        labels_data = validated_data.pop('labels', None) # handled by label_ids

        instance = super().update(instance, validated_data)

        if checklist_items_data is not None:
            # Simple replacement strategy for checklist items for now
            # Or smarter: update existing by ID?
            # For "Keep" style, usually we send the whole list.
            # But let's implementing a smart update if IDs are provided.

            # For simplicity in this Academy Project, let's just delete old and create new
            # unless specific ID handling is implemented.
            # But wait, if we delete, we lose "checked" state if the frontend didn't send it?
            # The frontend should send the full state.

            # Better approach: Clear and Re-create is safest for simple lists.
            instance.checklist_items.all().delete()
            for item_data in checklist_items_data:
                ChecklistItem.objects.create(note=instance, **item_data)

        return instance
