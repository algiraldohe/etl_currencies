from pydantic import BaseModel


class InitialTest(BaseModel):
    id: int
    name: str
    description: str