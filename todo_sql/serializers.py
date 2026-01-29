from rest_framework import serializers
from .models import Note, Label, ChecklistItem

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name']

    def validate_name(self, value):
        user = self.context['request'].user
        if Label.objects.filter(user=user, name=value).exists():
            raise serializers.ValidationError("Метка с таким названием уже существует.")
        return value

class ChecklistItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    note = serializers.PrimaryKeyRelatedField(queryset=Note.objects.all(), required=False)

    class Meta:
        model = ChecklistItem
        fields = ['id', 'text', 'is_checked', 'order', 'note']

    def validate_note(self, value):
        if value and value.user != self.context['request'].user:
            raise serializers.ValidationError("Вы не можете добавлять пункты в заметку другого пользователя.")
        return value

class NoteSerializer(serializers.ModelSerializer):
    checklist_items = ChecklistItemSerializer(many=True, required=False)
    labels = LabelSerializer(many=True, read_only=True)
    label_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Label.objects.all(), write_only=True, source='labels', required=False
    )
    reminder_date = serializers.DateTimeField(required=False, allow_null=True, input_formats=['%Y-%m-%dT%H:%M', 'iso-8601'])

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
            # Smart update
            existing_items = {item.id: item for item in instance.checklist_items.all()}
            posted_items = []

            for item_data in checklist_items_data:
                item_id = item_data.get('id')
                # If note is provided in nested data, remove it
                if 'note' in item_data:
                    del item_data['note']

                if item_id and item_id in existing_items:
                    # Update existing
                    item = existing_items.pop(item_id)
                    for attr, value in item_data.items():
                        setattr(item, attr, value)
                    item.save()
                    posted_items.append(item)
                else:
                    # Create new
                    if 'id' in item_data:
                        del item_data['id']
                    new_item = ChecklistItem.objects.create(note=instance, **item_data)
                    posted_items.append(new_item)

            # Delete remaining
            for item in existing_items.values():
                item.delete()

        return instance
