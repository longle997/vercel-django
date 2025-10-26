import json
from decimal import Decimal
from pathlib import Path

from django.db import transaction
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from .models import Product


def _data_file() -> Path:
    # products/signals.py -> products/ -> data/product.json
    return Path(__file__).resolve().parent / 'product.json'

@receiver(post_migrate)
def insert_initial_data(sender, **kwargs):
    """Insert initial data after migration is complete."""
    seed_products_if_empty()

def seed_products_if_empty():
    """
    After migrations, if the Product table is empty,
    load data from products/data/product.json and insert it.
    """

    data_path = _data_file()
    if not data_path.exists():
        # No file to load; silently skip (or log a warning)
        return

    with data_path.open('r', encoding='utf-8') as f:
        records = json.load(f) or []

    to_create = []
    for rec in records:
        # Map JSON fields to model fields
        # Your JSON has "_id" (string). We'll set the PK to that int
        # so your FE routes match (optional; you can omit if you prefer auto IDs).
        try:
            pk = int(rec.get('_id')) if rec.get('_id') is not None else None
        except (TypeError, ValueError):
            pk = None

        to_create.append(Product(
            id=pk,  # optional: let Django autogenerate if you prefer
            name=rec.get('name', ''),
            image=rec.get('image', ''),
            description=rec.get('description', ''),
            brand=rec.get('brand', ''),
            category=rec.get('category', ''),
            price=Decimal(str(rec.get('price', 0))),  # Decimal for money fields
            countInStock=int(rec.get('countInStock', 0) or 0),
            rating=float(rec.get('rating', 0) or 0),
            numReviews=int(rec.get('numReviews', 0) or 0),
        ))

    if not to_create:
        return

    # Single transaction; faster + safer
    with transaction.atomic():
        Product.objects.bulk_create(to_create, ignore_conflicts=True)
