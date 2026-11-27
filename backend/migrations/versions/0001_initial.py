from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "publications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("author", sa.String(255), nullable=False),
        sa.Column("publication_year", sa.Integer(), nullable=False),
        sa.Column("genre", sa.String(100), nullable=False),
        sa.Column("isbn", sa.String(17)),
        sa.CheckConstraint("publication_year > 0", name="ck_publications_year"),
        sa.UniqueConstraint("isbn", name="uq_publications_isbn"),
    )
    op.create_table(
        "readers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(150), nullable=False),
        sa.Column("card_number", sa.String(50), nullable=False),
        sa.UniqueConstraint("card_number", name="uq_readers_card_number"),
    )
    op.create_table(
        "copies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("publication_id", sa.Integer(), sa.ForeignKey("publications.id"), nullable=False),
        sa.Column("inventory_number", sa.String(50), nullable=False),
        sa.UniqueConstraint("inventory_number", name="uq_copies_inventory_number"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("reader_id", sa.Integer(), sa.ForeignKey("readers.id")),
        sa.UniqueConstraint("email", name="uq_users_email"),
        sa.UniqueConstraint("reader_id", name="uq_users_reader_id"),
        sa.CheckConstraint("role IN ('librarian', 'reader')", name="ck_users_role"),
        sa.CheckConstraint(
            "(role = 'librarian' AND reader_id IS NULL) OR "
            "(role = 'reader' AND reader_id IS NOT NULL)",
            name="ck_users_reader_role",
        ),
    )
    op.create_table(
        "loans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("copy_id", sa.Integer(), sa.ForeignKey("copies.id"), nullable=False),
        sa.Column("reader_id", sa.Integer(), sa.ForeignKey("readers.id"), nullable=False),
        sa.Column("loan_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("return_date", sa.Date()),
        sa.CheckConstraint("due_date >= loan_date", name="ck_loans_due_date"),
        sa.CheckConstraint("return_date >= loan_date", name="ck_loans_return_date"),
    )
    op.create_index(
        "uq_loans_open_copy",
        "loans",
        ["copy_id"],
        unique=True,
        postgresql_where=sa.text("return_date IS NULL"),
    )


def downgrade():
    op.drop_index("uq_loans_open_copy", table_name="loans")
    op.drop_table("loans")
    op.drop_table("users")
    op.drop_table("copies")
    op.drop_table("readers")
    op.drop_table("publications")
