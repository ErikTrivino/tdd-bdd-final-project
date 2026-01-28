######################################################################
# Models for Product Demo Service
######################################################################
import logging
from enum import Enum
from decimal import Decimal
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

db = SQLAlchemy()


def init_db(app):
    Product.init_db(app)


class DataValidationError(Exception):
    """Used for data validation errors"""


class Category(Enum):
    UNKNOWN = 0
    CLOTHS = 1
    FOOD = 2
    HOUSEWARES = 3
    AUTOMOTIVE = 4
    TOOLS = 5


class Product(db.Model):
    """Class that represents a Product"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Numeric, nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=True)
    category = db.Column(
        db.Enum(Category),
        nullable=False,
        server_default=Category.UNKNOWN.name,
    )

    def __repr__(self):  # pragma: no cover
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        logger.info("Creating %s", self.name)
        self.id = None
        db.session.add(self)
        db.session.commit()

    def update(self):
        logger.info("Updating %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID")  # pragma: no cover
        db.session.commit()

    def delete(self):
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "available": self.available,
            "category": self.category.name,
        }

    def deserialize(self, data):
        if not data:
            raise DataValidationError("No data provided")  # pragma: no cover

        try:
            self.name = data["name"]
            self.description = data["description"]
            self.price = Decimal(data["price"])

            if not isinstance(data["available"], bool):
                raise DataValidationError("Invalid type for available")  # pragma: no cover

            self.available = data["available"]
            self.category = Category[data["category"]]

        except KeyError as error:
            raise DataValidationError(f"Missing field: {error}") from error  # pragma: no cover
        except Exception as error:
            raise DataValidationError(str(error)) from error  # pragma: no cover

        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app: Flask):
        logger.info("Initializing database")
        db.init_app(app)
        app.app_context().push()
        db.create_all()

    @classmethod
    def all(cls):
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, product_id):
        logger.info("Processing lookup for id %s ...", product_id)
        return cls.query.get(product_id)

    @classmethod
    def find_by_name(cls, name):
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name).all()

    @classmethod
    def find_by_price(cls, price):
        logger.info("Processing price query for %s ...", price)
        value = Decimal(price) if isinstance(price, str) else price
        return cls.query.filter(cls.price == value).all()

    @classmethod
    def find_by_availability(cls, available=True):
        logger.info("Processing available query for %s ...", available)
        return cls.query.filter(cls.available == available).all()

    @classmethod
    def find_by_category(cls, category):
        logger.info("Processing category query for %s ...", category)

        # Acepta Category o string
        if isinstance(category, Category):
            category_enum = category
        else:
            try:
                category_enum = Category[category]
            except KeyError:
                return None

        return cls.query.filter(cls.category == category_enum).all()
