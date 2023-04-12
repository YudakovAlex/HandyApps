import string
import random

# The pas function takes in a length parameter and optional boolean parameters 
# to specify whether numbers, small letters, capital letters, and other symbols should be included.
def get_password(length,
        numbers=True,
        small_letters=True,
        capital_letter=True,
        other_symbols=True
        ):
    chars = ""
    # If a particular character type is set to True, add the corresponding characters to the character set.
    if numbers:
        chars += string.digits
    if small_letters:  
        chars += string.ascii_lowercase
    if capital_letter:  
        chars += string.ascii_uppercase
    if other_symbols:  
        chars += string.punctuation
    # Generate a list of random characters from the character set of specified length.
    pw_list = [random.choice(chars) for _ in range(length)]
    # Join the list of characters into a string password.
    pw = ''.join(pw_list)
    return pw

# The generate_passwords function generates a list of passwords using the get_password function. 
# It takes in two optional parameters: the number of passwords to generate (cnt) and the length of each password (lngth).
def generate_passwords(cnt=20,lngth=9):
    passwords = []
    for _ in range(cnt):
        passwords.append(get_password(lngth,other_symbols=True))
    return passwords

# Generate 20 passwords of length 9 with default settings and print them out.
for p in generate_passwords():
    print(p,"\n")
