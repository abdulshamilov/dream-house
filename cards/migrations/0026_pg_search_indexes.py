from django.db import migrations


def enable_pg_extensions(apps, schema_editor):
    """Enable pg_trgm/unaccent when using Postgres (safe no-op otherwise)."""
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        cursor.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


def create_search_indexes(apps, schema_editor):
    """Add GIN indexes to accelerate FTS and trigram search on cards."""
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS cards_card_search_vector_gin
            ON cards_card USING GIN (
                to_tsvector(
                    'simple',
                    coalesce(title, '') || ' ' || coalesce(address, '') || ' ' || coalesce(description, '')
                )
            );
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS cards_card_title_trgm_idx
            ON cards_card USING GIN (title gin_trgm_ops);
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS cards_card_address_trgm_idx
            ON cards_card USING GIN (address gin_trgm_ops);
            """
        )


def drop_search_indexes(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("DROP INDEX IF EXISTS cards_card_search_vector_gin;")
        cursor.execute("DROP INDEX IF EXISTS cards_card_title_trgm_idx;")
        cursor.execute("DROP INDEX IF EXISTS cards_card_address_trgm_idx;")


class Migration(migrations.Migration):

    dependencies = [
        ("cards", "0025_alter_callrequest_options_alter_card_options_and_more"),
    ]

    operations = [
        migrations.RunPython(enable_pg_extensions, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(create_search_indexes, reverse_code=drop_search_indexes),
    ]
