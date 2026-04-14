from enum import Enum


class ProductCategory(str, Enum):
    electronics = "electronics"
    clothing = "clothing"
    food = "food"
    home = "home"
    beauty = "beauty"
    sports = "sports"
    books = "books"
    other = "other"
