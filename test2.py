# test.py - Intentionally Buggy Code for Demo
# This file contains multiple bugs that the AI agent will fix

def add(a, b):
    return a + b

x = 1
y = 2
result = add(x, y)
print(f"Result: {result}")


def subtract(a, b):
    return a - b

z = 5
w = 3
result2 = subtract(z, w)
print(result2)

def multiply(x, y):
    """Multiply two numbers"""
    result = x * y
    return result

defined_var = 10
total = multiply(4, defined_var)
print(f"Total is {total}")

def divide(a, b):
    if b == 0:
        return None
    return a / b

numbers = [1, 2, 3, 4, 5]
for num in numbers:
    print(num)
