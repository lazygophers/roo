from tinydb import TinyDB, Query, where

db = TinyDB("db.json")

table = db.table("users")

table.insert({"name": "John", "age": 25})
table.insert({"name": "Mike", "age": 30})
table.insert({"name": "Mary", "age": 28})

print(table.search(Query().name == "John"))
print(table.contains(Query().name == "John" and Query().age == 25))
