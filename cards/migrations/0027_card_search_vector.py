from django.db import migrations


def add_generated_tsvector(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            ALTER TABLE cards_card
            ADD COLUMN IF NOT EXISTS search_vector tsvector GENERATED ALWAYS AS (
                setweight(to_tsvector('simple', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('simple', coalesce(address, '')), 'B') ||
                setweight(to_tsvector('simple', coalesce(description, '')), 'C')
            ) STORED;
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS cards_card_search_vector_gin
            ON cards_card USING GIN (search_vector);
            """
        )


def drop_generated_tsvector(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP INDEX IF EXISTS cards_card_search_vector_gin;")
        cursor.execute("ALTER TABLE cards_card DROP COLUMN IF EXISTS search_vector;")


class Migration(migrations.Migration):

    dependencies = [
        ("cards", "0026_pg_search_indexes"),
    ]

    operations = [
        migrations.RunPython(add_generated_tsvector, reverse_code=drop_generated_tsvector),
    ]
