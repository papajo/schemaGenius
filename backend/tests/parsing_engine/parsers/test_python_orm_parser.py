# backend/tests/parsing_engine/parsers/test_python_orm_parser.py
import unittest
from typing import Optional # For Mapped[Optional[str]]
from app.core.parsing_engine.parsers.python_orm_parser import parse_python_orm_input, _map_sqlalchemy_type_to_generic
from app.core.parsing_engine.intermediate_schema import SchemaISR, TableISR, ColumnISR, ConstraintDetail

class TestPythonOrmParser(unittest.TestCase):

    def test_map_sqla_type_to_generic_basic(self):
        self.assertEqual(_map_sqlalchemy_type_to_generic("Integer"), "INTEGER")
        self.assertEqual(_map_sqlalchemy_type_to_generic("String"), "STRING")
        self.assertEqual(_map_sqlalchemy_type_to_generic("String", [50]), "STRING")
        self.assertEqual(_map_sqlalchemy_type_to_generic("TEXT"), "TEXT")
        self.assertEqual(_map_sqlalchemy_type_to_generic("Boolean"), "BOOLEAN")
        self.assertEqual(_map_sqlalchemy_type_to_generic("DateTime"), "DATETIME")
        self.assertEqual(_map_sqlalchemy_type_to_generic("Enum", ["val1", "val2"]), "ENUM_TYPE")
        self.assertEqual(_map_sqlalchemy_type_to_generic("sa.Integer"), "INTEGER")
        self.assertEqual(_map_sqlalchemy_type_to_generic("sqlalchemy.orm.Mapped"), "STRING") # Fallback for Mapped itself

    def test_comprehensive_sqlalchemy_model(self):
        code = """
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Date, Float, Numeric, Enum as SQLAlchemyEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
# For older SQLAlchemy or different conventions, one might import types directly
from sqlalchemy import types
import datetime

# For Flask-SQLAlchemy style testing
class DB_dummy:
    Column = Column
    Integer = Integer
    String = String
    Text = Text
    Boolean = Boolean
    DateTime = DateTime
    Model = object # Dummy Model for base class testing
    ForeignKey = ForeignKey

db = DB_dummy() # Mock db object

Base = declarative_base()

class User(Base):
    __tablename__ = "users_table"
    '''This is a docstring for the User table.
    It should be captured as a table comment.'''

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="User primary key")
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True) # Optional implies nullable=True
    is_active: Mapped[bool] = mapped_column(default=True, comment="Is the user active?") # Type from Mapped
    created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow) # Type from Mapped
    bio = Column(types.Text, nullable=True, comment="User biography") # Using types.Text
    reputation = Column(Integer, default=0)
    profile_views = Column(db.Integer, default=0) # Using db.Integer

class Post(db.Model): # Example of Flask-SQLAlchemy style base
    __tablename__ = 'posts'
    # No class docstring for this one.

    post_id = db.Column(db.Integer, primary_key=True, comment="Post primary key")
    title = Column(String(200), nullable=False)
    content = Column(Text)
    # ForeignKey defined directly in Column
    author_user_id = Column(Integer, ForeignKey("users_table.user_id"), nullable=False)
    # Enum example using direct string values
    status = Column(SQLAlchemyEnum("draft", "published", "archived", name="post_status_enum"), default="draft")
    # __table_args__ = (UniqueConstraint('title', 'author_user_id', name='uq_post_title_author'),) # Not parsed yet
"""
        schema_isr = parse_python_orm_input(code)
        self.assertEqual(len(schema_isr.tables), 2, "Should parse two tables")

        # --- User Table Assertions ---
        user_table = next((t for t in schema_isr.tables if t.name == "users_table"), None)
        self.assertIsNotNone(user_table, "User table should be parsed")
        self.assertEqual(user_table.comment.strip(), "This is a docstring for the User table.\n    It should be captured as a table comment.")
        self.assertEqual(len(user_table.columns), 8, f"User table should have 8 columns, found {[c.name for c in user_table.columns]}")

        # user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="User primary key")
        user_id_col = next(c for c in user_table.columns if c.name == "user_id")
        self.assertEqual(user_id_col.generic_type, "INTEGER")
        self.assertTrue(any(con.type == "PRIMARY_KEY" for con in user_id_col.constraints))
        self.assertTrue(any(con.type == "AUTO_INCREMENT" for con in user_id_col.constraints))
        self.assertEqual(user_id_col.comment, "User primary key")

        # username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
        username_col = next(c for c in user_table.columns if c.name == "username")
        self.assertEqual(username_col.generic_type, "STRING") # String(50)
        self.assertTrue(any(con.type == "UNIQUE" for con in username_col.constraints))
        self.assertTrue(any(con.type == "NOT_NULL" for con in username_col.constraints))

        # email: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
        email_col = next(c for c in user_table.columns if c.name == "email")
        self.assertEqual(email_col.generic_type, "STRING") # String(100)
        self.assertFalse(any(con.type == "NOT_NULL" for con in email_col.constraints)) # Optional implies nullable=True
        self.assertTrue(any(con.type == "UNIQUE" for con in email_col.constraints))

        # is_active: Mapped[bool] = mapped_column(default=True, comment="Is the user active?")
        is_active_col = next(c for c in user_table.columns if c.name == "is_active")
        self.assertEqual(is_active_col.generic_type, "BOOLEAN")
        default_constr_active = next(c for c in is_active_col.constraints if c.type == "DEFAULT")
        self.assertEqual(default_constr_active.details.get("value"), True)
        self.assertEqual(is_active_col.comment, "Is the user active?")

        # created_at: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.utcnow)
        created_at_col = next(c for c in user_table.columns if c.name == "created_at")
        self.assertEqual(created_at_col.generic_type, "DATETIME") # from datetime.datetime hint
        self.assertTrue(any(con.type == "DEFAULT" for con in created_at_col.constraints)) # default value is a func call, hard to assert specific value

        # bio = Column(types.Text, nullable=True, comment="User biography")
        bio_col = next(c for c in user_table.columns if c.name == "bio")
        self.assertEqual(bio_col.generic_type, "TEXT") # types.Text
        self.assertFalse(any(con.type == "NOT_NULL" for con in bio_col.constraints)) # nullable=True
        self.assertEqual(bio_col.comment, "User biography")

        # reputation = Column(Integer, default=0)
        reputation_col = next(c for c in user_table.columns if c.name == "reputation")
        self.assertEqual(reputation_col.generic_type, "INTEGER")
        default_constr_rep = next(c for c in reputation_col.constraints if c.type == "DEFAULT")
        self.assertEqual(default_constr_rep.details.get("value"), 0)

        # profile_views = Column(db.Integer, default=0)
        profile_views_col = next(c for c in user_table.columns if c.name == "profile_views")
        self.assertEqual(profile_views_col.generic_type, "INTEGER") # db.Integer
        default_constr_pv = next(c for c in profile_views_col.constraints if c.type == "DEFAULT")
        self.assertEqual(default_constr_pv.details.get("value"), 0)


        # --- Post Table Assertions ---
        post_table = next((t for t in schema_isr.tables if t.name == "posts"), None)
        self.assertIsNotNone(post_table, "Post table should be parsed")
        self.assertIsNone(post_table.comment, "Post table should have no docstring comment") # No docstring
        self.assertEqual(len(post_table.columns), 5, f"Post table should have 5 columns, found {[c.name for c in post_table.columns]}")

        # post_id = db.Column(db.Integer, primary_key=True, comment="Post primary key")
        post_id_col = next(c for c in post_table.columns if c.name == "post_id")
        self.assertEqual(post_id_col.generic_type, "INTEGER")
        self.assertTrue(any(con.type == "PRIMARY_KEY" for con in post_id_col.constraints))
        self.assertEqual(post_id_col.comment, "Post primary key")

        # author_user_id = Column(Integer, ForeignKey("users_table.user_id"), nullable=False)
        author_user_id_col = next(c for c in post_table.columns if c.name == "author_user_id")
        self.assertEqual(author_user_id_col.generic_type, "INTEGER") # Type from Column(Integer,...)
        self.assertTrue(any(con.type == "NOT_NULL" for con in author_user_id_col.constraints))
        fk_constraint = next(c for c in author_user_id_col.constraints if c.type == "FOREIGN_KEY")
        self.assertIsNotNone(fk_constraint)
        self.assertEqual(fk_constraint.details.get("references_table"), "users_table")
        self.assertEqual(fk_constraint.details.get("references_column"), "user_id")

        # status = Column(SQLAlchemyEnum("draft", "published", "archived", name="post_status_enum"), default="draft")
        status_col = next(c for c in post_table.columns if c.name == "status")
        self.assertEqual(status_col.generic_type, "ENUM_TYPE")
        enum_val_constr = next(c for c in status_col.constraints if c.type == "ENUM_VALUES")
        self.assertIsNotNone(enum_val_constr)
        self.assertEqual(enum_val_constr.details.get("values"), ["draft", "published", "archived"])
        default_constr_status = next(c for c in status_col.constraints if c.type == "DEFAULT")
        self.assertEqual(default_constr_status.details.get("value"), "draft")


    def test_no_sqlalchemy_models_in_code(self):
        code = "def some_function(): return 1\nclass MyObject:\n    pass"
        schema_isr = parse_python_orm_input(code)
        self.assertEqual(len(schema_isr.tables), 0, "Should parse zero tables if no SQLAlchemy models")

    def test_invalid_python_syntax_input(self):
        code = "class User(Base:\n    name = Column(String)" # Invalid syntax
        with self.assertRaisesRegex(ValueError, "Invalid Python syntax"):
            parse_python_orm_input(code)

if __name__ == "__main__":
    unittest.main()
