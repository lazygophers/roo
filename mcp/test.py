from tinydb import TinyDB, Query

db = TinyDB("db.json")

db.insert({"name": "John", "age": 25})
db.insert({"name": "Mike", "age": 30})
db.insert({"name": "Mary", "age": 28})

print(db.search(Query().name == "John"))
