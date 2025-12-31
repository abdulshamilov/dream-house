# Generated manually to remove obsolete login_code field

from django.db import migrations


def remove_login_code_column(apps, schema_editor):
    """Remove login_code column if it exists"""
    from django.db import connection
    with connection.cursor() as cursor:
        # Check if column exists
        cursor.execute("PRAGMA table_info(users_user)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'login_code' in columns:
            # SQLite doesn't support DROP COLUMN directly, need to recreate table
            # But first, let's try to just set it nullable
            cursor.execute("""
                CREATE TABLE users_user_new AS 
                SELECT id, password, last_login, is_superuser, name, is_active, 
                       is_staff, phone_number, profile_photo
                FROM users_user
            """)
            cursor.execute("DROP TABLE users_user")
            cursor.execute("ALTER TABLE users_user_new RENAME TO users_user")


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_loginotp'),
    ]

    operations = [
        migrations.RunPython(remove_login_code_column, migrations.RunPython.noop),
    ]
