def productEntity(item) -> dict:
  return {
    "product_name": item["product_name"],
    "price": item["price"],
    "stock_count": item["stock_count"],
  }

def productsEntity(entity) -> list:
  return [productEntity(item) for item in entity]