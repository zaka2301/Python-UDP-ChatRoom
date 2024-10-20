class RC4_:
    def __init__(self, key):
        self.key = list(key.encode())
        self.length = len(key)

    def KSA(self): #Key-scheduling algorithm
        S = list(range(256))
        j = 0
        for i in range(256):
            j = (j + S[i] + self.key[i % self.length]) % 256
            S[i], S[j] = S[j], S[i]

        return S

    def PRGA(self, text): #Pseudo-random generation algorithm
        i = 0
        j = 0
        K = []
        S = self.KSA()
        length = 0
        for l in text:
            length += 1
        while i < length:
            i = (i + 1) % 256
            j = (j + S[i]) % 256
            S[i], S[j] = S[j], S[i]
            t = (S[i] + S[j]) % 256
            K.append(S[t])
        return K

    def convert(self, text):
        if isinstance(text, str):
            text = text.encode()
        keystream = self.PRGA(text)
        result = bytearray()
        i = 0
        for byte in text:
            result.append(byte ^ keystream[i])
            i += 1
        return result

    # encrypt and decrypt function return a string
    def encrypt(self, text):
        return str(self.convert(text).hex())

    def decrypt(self, text):
        return self.convert(bytearray.fromhex(text)).decode()



if __name__ == "__main__":
    key = "Key"
    plaintext = "2301"
    RC4 = RC4_(key)

    print(f"Key: {key}")
    print(f"Plaintext: {plaintext}")

    ciphertext = RC4.encrypt(plaintext)
    print(f"Ciphertext: {ciphertext}")

    ciphertext2 = RC4.encrypt(ciphertext)
    print(f"Ciphertex2: {ciphertext2}")

    ciphertext = RC4.decrypt(ciphertext2)
    print(f"Ciphertext: {ciphertext}")

    decrypted = RC4.decrypt(ciphertext)
    print(f"Decrypted: {decrypted}")
    