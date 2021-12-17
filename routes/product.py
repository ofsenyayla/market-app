from fastapi import APIRouter
from models.product import Product
from config.db import conn
from schemas.product import productsEntity

product = APIRouter()


@product.get("/products")
async def get_products():
  return productsEntity(conn.local.product.find())


@product.post("/products/add")
async def add_product(data: dict):
  # check if the user is staff
  username = data["username"]
  user = conn.local.user.find_one({"username":username})
  if not user:
    return {"error": "this user cannot be found"}

  else:
    if user["is_staff"] == False:
      return {"error": "you cannot add new product"}

    else:
      product_name = data["product_name"]
      product = conn.local.product.find_one({"product_name":product_name})

      # create new product
      if not product:
        product_dict = {
          "product_name": product_name,
          "price": data["price"],
          "stock_count": data["stock_count"]
        }
        conn.local.product.insert_one(product_dict)

        return {"success": "your products are successfully added"}

      # update existing product's stock count and price
      else:
        conn.local.product.find_one_and_update(
          {"product_name":product_name},
          {"$set":{
            "price": data["price"],
            "stock_count": product["stock_count"] + data["stock_count"]
          }})

        return {"success": "your product is successfully updated"}


@product.post("/products/delete")
async def delete_product(data: dict):
  # check if the user is staff
  username = data["username"]
  user = conn.local.user.find_one({"username":username})
  if not user:
    return {"error": "this user cannot be found"}

  else:
    product_name = data["product_name"]
    product = conn.local.product.find_one({"product_name":product_name})

    if not product:
      return {"error": "we cannot found your products"}

    if "stock_count" in data.keys():
      if data["stock_count"] > product["stock_count"]:
        conn.local.product.delete_one({"product_name":product_name})
        return {"success": "your product is successfully deleted"}

      # decrease the existing stock count
      conn.local.product.find_one_and_update(
          {"product_name": data["product_name"]},
          {"$set":{
            "stock_count": product["stock_count"] - data["stock_count"]
          }})
      return {"success": "your stock count is successfully updated"}

    else:
      conn.local.product.delete_one({"product_name":product_name})
      return {"success": "your product is successfully deleted"}


@product.post("/products/get-stock")
async def get_stock(data: dict):
  product_name = data["product_name"]
  product = conn.local.product.find_one({"product_name":product_name})

  if product:
    return {product_name: product["stock_count"]}

  else:
    return {"error": "we cannot found this product"}


@product.post("/products/get-price")
async def get_price(data: dict):
  product_name = data["product_name"]
  product = conn.local.product.find_one({"product_name":product_name})

  if product:
    return {product_name: str(product["price"]) + " $"}

  else:
    return {"error": "we cannot found this product"}