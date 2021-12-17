from pydantic import BaseModel

class User(BaseModel):
  name: str
  username: str
  password: str
  email: str
  is_staff: bool = False
