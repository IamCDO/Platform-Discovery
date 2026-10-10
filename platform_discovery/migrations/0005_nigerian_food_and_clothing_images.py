from django.db import migrations


FOOD_IMAGE = 'https://images.unsplash.com/photo-1664992960082-0ea299a9c53e?auto=format&fit=crop&w=900&q=80'
CLOTHING_IMAGE = 'https://images.unsplash.com/photo-1788035962539-a1d6ef60ec48?auto=format&fit=crop&w=900&q=80'


def update_default_images(apps, schema_editor):
    BusinessCategory = apps.get_model('platform_discovery', 'BusinessCategory')
    Business = apps.get_model('platform_discovery', 'Business')

    BusinessCategory.objects.filter(
        slug='food-drinks',
        image_url='https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80',
    ).update(image_url=FOOD_IMAGE)
    BusinessCategory.objects.filter(
        slug='clothing',
        image_url='https://images.unsplash.com/photo-1529139574466-a303027c1d8b?auto=format&fit=crop&w=900&q=80',
    ).update(image_url=CLOTHING_IMAGE)

    Business.objects.filter(
        category__slug='food-drinks',
        image_url='https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=900&q=80',
    ).update(image_url=FOOD_IMAGE)
    Business.objects.filter(
        category__slug='clothing',
        image_url='https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=900&q=80',
    ).update(image_url=CLOTHING_IMAGE)


class Migration(migrations.Migration):

    dependencies = [
        ('platform_discovery', '0004_product_image_url'),
    ]

    operations = [
        migrations.RunPython(update_default_images, migrations.RunPython.noop),
    ]