from fastapi import APIRouter
from models.product import Product
from config.db import conn
from schemas.product import productsEntity
from fastapi import HTTPException

product = APIRouter()


@product.get("/products/")
async def get_products():
  return productsEntity(conn.local.product.find())


@product.post("/products/add/{username}/")
async def add_product(data: dict, username):
  # check if the user is staff
  user = conn.local.user.find_one({"username":username})
  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    if user["is_staff"] == False:
      raise HTTPException(status_code=401, detail={"ERROR": "you cannot add new product"})

    else:
      product_name = data["product_name"]
      product = conn.local.product.find_one({"product_name":product_name})

      # create new product
      if not product:
        try:
          float(data["price"])
          int(data["stock_count"])

        except:
          raise HTTPException(status_code=400, detail={"ERROR": "invalid price or stock count"})

        if data["price"] <= 0 or data["stock_count"] <= 0:
          raise HTTPException(status_code=400, detail={"ERROR": "invalid price or stock count"})

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


@product.delete("/products/delete/{username}/")
async def delete_product(data: dict, username):
  # check if the user is staff
  user = conn.local.user.find_one({"username":username})
  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    if user["is_staff"] == False:
      raise HTTPException(status_code=401, detail={"ERROR": "you cannot delete product"})

    else:
      product_name = data["product_name"]
      product = conn.local.product.find_one({"product_name":product_name})

      if not product:
        raise HTTPException(status_code=404, detail={"ERROR": "this product cannot be found"})

      if "stock_count" in data.keys():
        if data["stock_count"] > product["stock_count"]:
          conn.local.product.delete_one({"product_name":product_name})
          return {"success": "the product is successfully deleted"}

        # decrease the existing stock count
        conn.local.product.find_one_and_update(
            {"product_name": data["product_name"]},
            {"$set":{
              "stock_count": product["stock_count"] - data["stock_count"]
            }})
        return {"success": "the stock count is successfully updated"}

      else:
        conn.local.product.delete_one({"product_name":product_name})
        return {"success": "the product is successfully deleted"}


@product.get("/products/get-stock/{product_name}/")
async def get_stock(product_name):
  product = conn.local.product.find_one({"product_name": product_name})

  if product:
    return {product_name: product["stock_count"]}

  else:
    raise HTTPException(status_code=404, detail={"ERROR": "this product cannot be found"})


@product.get("/products/get-price/{product_name}/")
async def get_price(product_name):
  product = conn.local.product.find_one({"product_name":product_name})

  if product:
    return {product_name: str(product["price"]) + " $"}

  else:
    raise HTTPException(status_code=404, detail={"ERROR": "this product cannot be found"})