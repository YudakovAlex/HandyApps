import random
def pas(length,
        numbers=True,
        small_letters=True,
        capital_letter=True,
        other_symbols=True
        ):
    pw = str()
    chars = ""
    if numbers:
        chars += "1234567890"
    if small_letters:  
        chars += "qwertyuiopasdfghjklzxcvbnm"
    if capital_letter:  
        chars += "QWERTYUIOPASDFGHJKLZXCVBNM"
    if other_symbols:  
        chars += ".,!@#$%^&*<>"
        
    for i in range(length):
        pw = pw + random.choice(chars)
    return pw


def gen_pasw(cnt=10,lngth=12):
    pw = []
    
    for i in range(cnt):
        pw.append(pas(lngth))
    return pw
        
print(gen_pasw())