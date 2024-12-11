"# tcg_frontend"

CREATE DATA

py manage.py shell

from store.models import Item

Item.objects.create(name="Item 1", price=10.99)

Item.objects.create(name="Item 2", price=15.49)



VIEW DATABASE:

py manage.py shell

from store.models import Item

items = Item.objects.all()

for item in items:

    print(f"ID: {item.id}, Name: {item.name}")
