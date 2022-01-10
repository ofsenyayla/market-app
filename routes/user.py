from fastapi import APIRouter
from models.user import User
from config.db import conn
from schemas.user import usersEntity
from fastapi import HTTPException

user = APIRouter()

@user.get("/")
async def index():
  return {"home page": "this is the index file. you can navigate /docs /users or /products"}

@user.get("/users/")
async def get_users():
  return usersEntity(conn.local.user.find())

@user.post("/users/register/")
async def register_user(user: User):
  # TODO: username will be unique
  dict_user = dict(user)
  document = conn.local.user.find_one({"username": dict_user['username']})
  if document:
    raise HTTPException(status_code=400, detail={"ERROR": "this username is already exists"})

  document = conn.local.user.find_one({"email": dict_user['email']})
  if document:
    raise HTTPException(status_code=400, detail={"ERROR": "this email is already exists"})

  dict_user["wallet"] = 0.0
  dict_user["basket"] = {}
  dict_user["basket_total"] = 0.0
  conn.local.user.insert_one(dict_user)
  return {"message": "user created successfully"}


@user.post("/users/login/")
async def login_user(data: dict):
  username = data["username"]
  password = data["password"]
  user = conn.local.user.find_one({"username":username})

  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    if user["password"] == password:
      return {"successful": "login is successful"}

    else:
      raise HTTPException(status_code=404, detail={"ERROR": "username or password is wrong"})


@user.post("/users/deposit-money/{username}/")
async def deposit_money(data: dict, username):
  user = conn.local.user.find_one({"username":username})
  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  try:
    float(data["deposit_count"])
    if data["deposit_count"] < 0:
      raise HTTPException(status_code=400, detail={"ERROR": "invalid deposit count"})
  
  except:
    raise HTTPException(status_code=400, detail={"ERROR": "invalid deposit count"})

  else:
    conn.local.user.find_one_and_update(
      {"username": username},
      {"$set":{
        "wallet": user["wallet"] + data["deposit_count"]
      }})
    return {"success": "your money is successfully updated"}


@user.get("/users/check-wallet/{username}/")
async def check_wallet(username):
  user = conn.local.user.find_one({"username":username})

  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    return {"your balance": str(user["wallet"]) + " $"}


@user.post("/users/add-basket/{username}/")
async def add_basket(data: dict, username):
  user = conn.local.user.find_one({"username":username})

  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    product_name = data["product_name"]
    product = conn.local.product.find_one({"product_name":product_name})

    if product:
      if product["stock_count"] < 1:
        conn.local.product.delete_one({"product_name":product_name})
        return {"error": "this product's stock is currently not available"}

      conn.local.product.find_one_and_update(
        {"product_name": product_name},
        {"$set":{
          "stock_count": product["stock_count"] - 1
        }})

      basket = user["basket"]
      if product_name in basket.keys():
        basket[product_name] += 1
      else:
        basket[product_name] = 1

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
      raise HTTPException(status_code=400, detail={"ERROR": "this product is currently not available"})


@user.get("/users/basket-total/{username}/")
async def basket_total(username):
  user = conn.local.user.find_one({"username":username})

  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    return {"current total price": str(user["basket_total"]) + " $"}


@user.get("/users/basket-content/{username}/")
async def basket_content(username):
  user = conn.local.user.find_one({"username":username})

  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    return {"current basket": user["basket"]}


@user.get("/users/buy-basket-content/{username}/")
async def buy_basket_content(username):
  user = conn.local.user.find_one({"username":username})

  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    wallet = user["wallet"]
    basket_total = user["basket_total"]

    if basket_total > wallet:
      return {"error": "your balance is not enough"}

    else:
      if user["basket"] != {}:
        conn.local.user.find_one_and_update(
          {"username": username},
          {"$set":{
            "basket": {},
            "basket_total": 0,
            "wallet": wallet - basket_total
          }})
        
        return {"success": "you have successfully purchased your basket content"}
      
      else:
        return {"error": "your basket is empty"}

    
@user.delete("/users/delete-basket/{username}/")
async def delete_basket(username):
  user = conn.local.user.find_one({"username":username})

  if not user:
    raise HTTPException(status_code=404, detail={"ERROR": "this user cannot be found"})

  else:
    basket = user["basket"]
    if basket != {}:
      for p in basket.keys():
        conn.local.product.find_one_and_update(
          {"product_name": p},
          {"$set":{
            "stock_count": conn.local.product.find_one({"product_name":p})["stock_count"] + basket[p]
          }})

      conn.local.user.find_one_and_update(
          {"username": username},
          {"$set":{
            "basket": {},
            "basket_total": 0,
          }})

      return {"success": "your basket is successfully deleted"}
    
    else:
      return {"error": "your basket is empty"}