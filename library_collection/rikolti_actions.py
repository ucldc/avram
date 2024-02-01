
import django.contrib.messages as messages

def harvest_collection(modeladmin, request, queryset):
    """Harvest the selected collections"""
    status = []
    for collection in queryset:
        print(collection.name)
        status.append(True)
    msg = f"got em! {len(status)} collection: {bool(all(status))}"
    modeladmin.message_user(request, msg, level=messages.SUCCESS)

harvest_collection.short_description = 'Harvest the collection[s]'