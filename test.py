def hello(name):
    message = f"Hi {name}!" if name == "Alice" else "Hello!"
    print(message)


for i in range(10):
    hello("Bob")
