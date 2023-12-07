import string
import secrets  # More secure than random for password generation

def get_password(length, include_numbers=True, include_small_letters=True,
                 include_capitals=True, include_symbols=True):
    """
    Generate a random password with the given length and character inclusion settings.
    """
    if length <= 0 or not any([include_numbers, include_small_letters, include_capitals, include_symbols]):
        raise ValueError("Invalid parameters for password generation.")

    chars = ""
    if include_numbers:
        chars += string.digits
    if include_small_letters:
        chars += string.ascii_lowercase
    if include_capitals:
        chars += string.ascii_uppercase
    if include_symbols:
        chars += string.punctuation

    while True:
        password = ''.join(secrets.choice(chars) for _ in range(length))
        if (include_numbers and not any(c in string.digits for c in password)):
            continue
        if (include_small_letters and not any(c in string.ascii_lowercase for c in password)):
            continue
        if (include_capitals and not any(c in string.ascii_uppercase for c in password)):
            continue
        if (include_symbols and not any(c in string.punctuation for c in password)):
            continue
        return password

def generate_passwords(count=20, length=12):
    """
    Generate a list of random passwords.
    """
    return [get_password(length) for _ in range(count)]

# Generate and print passwords
for password in generate_passwords():
    print(password + "\n")
