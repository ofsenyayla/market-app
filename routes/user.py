from fastapi import APIRouter
from models.user import User
from config.db import conn
from schemas.user import usersEntity

user = APIRouter()

@user.get("/")
async def index():
  return {"home page": "this is the index file. you can navigate /docs /users or /products"}

@user.post("/users/register")
async def register_user(user: User):
  # TODO: username will be unique
  dict_user = dict(user)
  dict_user["wallet"] = 0.0
  dict_user["basket"] = []
  dict_user["basket_total"] = 0.0
  conn.local.user.insert_one(dict_user)
  return {"message": "user created successfully"}


@user.post("/users/login")
async def login_user(data: dict):
  username = data["username"]
  password = data["password"]
  user = conn.local.user.find_one({"username":username})

  if not user:
    return {"wrong username":"this username cannot be found"}

  else:
    if user["password"] == password:
      return {"successful": "login is successful"}

    else:
      return {"error":"username or password is wrong"}


@user.post("/users/deposit-money")
async def deposit_money(data: dict):
  username = data["username"]
  user = conn.local.user.find_one({"username":username})
  if not user:
    return {"error": "this user cannot be found"}

  else:
    conn.local.user.find_one_and_update(
      {"username": username},
      {"$set":{
        "wallet": user["wallet"] + data["deposit_count"]
      }})
    return {"success": "your money is successfully updated"}


@user.post("/users/check-wallet")
async def check_wallet(data: dict):
  username = data["username"]
  user = conn.local.user.find_one({"username":username})

  if not user:
    return {"error": "this user cannot be found"}

  else:
    return {"your balance": str(user["wallet"]) + " $"}


@user.post("/users/add-basket")
async def add_basket(data: dict):
  username = data["username"]
  user = conn.local.user.find_one({"username":username})

  if not user:
    return {"error": "this user cannot be found"}

  else:
    product_name = data["product_name"]
    product = conn.local.product.find_one({"product_name":product_name})

    if product:
      conn.local.product.find_one_and_update(
        {"product_name": product_name},
        {"$set":{
          "stock_count": product["stock_count"] - 1
        }})

      basket = user["basket"]
      basket.append(product_name)

      basket_total = user["basket_total"]
      basket_total += product["price"]

      conn.local.user.find_one_and_update(
        {"username": username},
        {"$set":{
          "basket": basket,
          "basket_total": basket_total
        }})

      return {"success": "this product is successfully added to your basket"}

    else:
      return {"error": "this product is currently unavailable"}


@user.post("/users/basket-total")
async def basket_total(data: dict):
  username = data["username"]
  user = conn.local.user.find_one({"username":username})

  if not user:
    return {"error": "this user cannot be found"}

  else:
    return {"current total price": str(user["basket_total"]) + " $"}


@user.post("/users/basket-content")
async def basket_content(data: dict):
  username = data["username"]
  user = conn.local.user.find_one({"username":username})

  if not user:
    return {"error": "this user cannot be found"}

  else:
    return {"current basket": user["basket"]}


@user.post("/users/buy-basket-content")
async def buy_basket_content(data: dict):
  username = data["username"]
  user = conn.local.user.find_one({"username":username})

  if not user:
    return {"error": "this user cannot be found"}

  else:
    wallet = user["wallet"]
    basket_total = user["basket_total"]

    if basket_total > wallet:
      return {"error": "your balance is not enough"}

    else:
      conn.local.user.find_one_and_update(
        {"username": username},
        {"$set":{
          "basket": [],
          "basket_total": 0,
          "wallet": wallet - basket_total
        }})
      
      return {"success": "you are successfully purchased your basket content"}

    
@user.post("/users/delete-basket")
async def delete_basket(data: dict):
  username = data["username"]
  user = conn.local.user.find_one({"username":username})

  if not user:
    return {"error": "this user cannot be found"}

  else:
    basket = user["basket"]
    for p in basket:
      conn.local.product.find_one_and_update(
        {"product_name": p},
        {"$set":{
          "stock_count": conn.local.product.find_one({"product_name":p})["stock_count"] + 1
        }})

    conn.local.user.find_one_and_update(
        {"username": username},
        {"$set":{
          "basket": [],
          "basket_total": 0,
        }})

    return {"success": "your basket is successfully deleted"}