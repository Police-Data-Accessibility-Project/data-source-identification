from alembic import op
import sqlalchemy as sa

def switch_enum_type(
        table_name,
        column_name,
        enum_name,
        new_enum_values,
        drop_old_enum=True,
        check_constraints_to_drop: list[str] = None,
):
    """
    Switches an ENUM type in a PostgreSQL column by:
    1. Renaming the old enum type.
    2. Creating the new enum type with the same name.
    3. Updating the column to use the new enum type.
    4. Dropping the old enum type.

    :param table_name: Name of the table containing the ENUM column.
    :param column_name: Name of the column using the ENUM type.
    :param enum_name: Name of the ENUM type in PostgreSQL.
    :param new_enum_values: List of new ENUM values.
    :param drop_old_enum: Whether to drop the old ENUM type.
    """

    # 1. Drop check constraints that reference the enum
    if check_constraints_to_drop is not None:
        for constraint in check_constraints_to_drop:
            op.execute(f'ALTER TABLE "{table_name}" DROP CONSTRAINT IF EXISTS "{constraint}"')


    # Rename old enum type
    old_enum_temp_name = f"{enum_name}_old"
    op.execute(f'ALTER TYPE "{enum_name}" RENAME TO "{old_enum_temp_name}"')

    # Create new enum type with the updated values
    new_enum_type = sa.Enum(*new_enum_values, name=enum_name)
    new_enum_type.create(op.get_bind())

    # Alter the column type to use the new enum type
    op.execute(f'ALTER TABLE "{table_name}" ALTER COLUMN "{column_name}" TYPE "{enum_name}" USING "{column_name}"::text::{enum_name}')

    # Drop the old enum type
    if drop_old_enum:
        op.execute(f'DROP TYPE "{old_enum_temp_name}"')

def alter_enum_value(
        enum_name,
        old_value,
        new_value
):
    """
    Changes one value of an enum type
    """
    op.execute(f"ALTER TYPE {enum_name} RENAME VALUE '{old_value}' TO '{new_value}'")

def created_at_column():
    """Returns a standard `created_at` column."""
    return sa.Column(
        'created_at',
        sa.DateTime(),
        server_default=sa.text('now()'),
        nullable=False
    )

def updated_at_column():
    """Returns a standard `updated_at` column."""
    return sa.Column(
        'updated_at',
        sa.DateTime(),
        server_default=sa.text('now()'),
        server_onupdate=sa.text('now()'),
        nullable=False
    )
