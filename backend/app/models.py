from pydantic import BaseModel
from typing import List

class Magazine(BaseModel):
    id: int
    title: str
    author: str
    publication_date: str
    category: str

class MagazineContent(BaseModel):
    id: int
    magazine_id: int
    content: str
    vector_representation: List[float]

class MagazineWithContent(Magazine):
    content: str