a = ["/1/1/", "/1/2/2"]

a = [i[2:] if i.startswith("/1") else i for i in a]

print(a)
