import random
def pas(length):
    pw = str()
    chars = "1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM.,!@#$%^&*<>"
    for i in range(length):
        pw = pw + random.choice(chars)
    return pw

for i in range(10):
    pw = pas(12)
    print(pw)