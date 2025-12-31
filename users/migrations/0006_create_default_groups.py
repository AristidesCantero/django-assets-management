from django.db import migrations

def create_default_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    admin_group, _ = Group.objects.get_or_create(name='ADMIN')
    user_group, _ = Group.objects.get_or_create(name='MANAGER')


    # Permisos del admin (ejemplo)
    #admin_permissions = Permission.objects.filter(
    #    codename__in=[
    #        'add_user',
    #        'change_user',
    #        'view_user',
    #        'delete_user',
    #    ]
    #)

    #admin_group.permissions.set(admin_permissions)

def remove_default_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['ADMIN', 'MANAGER']).delete()

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_historicaluser_date_joined_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_default_groups, remove_default_groups),
    ]