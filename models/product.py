from pydantic import BaseModel

class Product(BaseModel):
  product_name: str
  price: float
  stock_count: int
