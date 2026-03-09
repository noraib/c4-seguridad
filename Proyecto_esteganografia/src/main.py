from cripto.aes import generate_key, encrypt_message, decrypt_message


def main():

    message = "Mensaje secreto"

    key = generate_key()

    encrypted = encrypt_message(message, key)

    decrypted = decrypt_message(encrypted, key)

    print("Original:", message)
    print("Encrypted:", encrypted)
    print("Decrypted:", decrypted)


if __name__ == "__main__":
    main()