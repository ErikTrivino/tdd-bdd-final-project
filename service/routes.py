######################################################################
# Product Store Service Routes
######################################################################
import logging
from flask import jsonify, request, abort, url_for
from service.models import Product, DataValidationError
from service.common import status
from . import app

logger = logging.getLogger("flask.app")


######################################################################
# HEALTH CHECK
######################################################################
@app.route("/health")
def healthcheck():
    return jsonify(status=200, message="OK"), status.HTTP_200_OK


######################################################################
# HOME PAGE
######################################################################
@app.route("/")
def index():
    return app.send_static_file("index.html")


######################################################################
# UTIL
######################################################################
def check_content_type(content_type):
    if "Content-Type" not in request.headers:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    if request.headers["Content-Type"] != content_type:
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)


######################################################################
# CREATE
######################################################################
@app.route("/products", methods=["POST"])
def create_products():
    check_content_type("application/json")

    try:
        product = Product()
        product.deserialize(request.get_json())
        product.create()
    except DataValidationError:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid product data")

    location_url = url_for("get_product", product_id=product.id, _external=True)
    return (
        jsonify(product.serialize()),
        status.HTTP_201_CREATED,
        {"Location": location_url},
    )


######################################################################
# LIST
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    name = request.args.get("name")
    category = request.args.get("category")
    available = request.args.get("available")

    if name:
        products = Product.find_by_name(name)

    elif category:
        products = Product.find_by_category(category)
        if products is None:
            abort(status.HTTP_400_BAD_REQUEST, "Invalid category")

    elif available is not None:
        if available.lower() not in ["true", "false"]:
            abort(status.HTTP_400_BAD_REQUEST, "Invalid availability")
        products = Product.find_by_availability(available.lower() == "true")

    else:
        products = Product.all()

    return jsonify([p.serialize() for p in products]), status.HTTP_200_OK


######################################################################
# READ
######################################################################
@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, "Product not found")
    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# UPDATE
######################################################################
@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    check_content_type("application/json")
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, "Product not found")

    try:
        product.deserialize(request.get_json())
        product.update()
    except DataValidationError:
        abort(status.HTTP_400_BAD_REQUEST, "Invalid product data")

    return jsonify(product.serialize()), status.HTTP_200_OK


######################################################################
# DELETE
######################################################################
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    logger.info("Processing delete for id %s ...", product_id)
    product = Product.find(product_id)
    if not product:
        abort(status.HTTP_404_NOT_FOUND, "Product not found")

    product.delete()
    return "", status.HTTP_204_NO_CONTENT
