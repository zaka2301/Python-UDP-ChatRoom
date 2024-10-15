import binascii

def calculate_checksum(message):
    return binascii.crc32(message.encode()) & 0xffffffff  # Pastikan hasil CRC32 positif


message = "hai ibay"

print(int(calculate_checksum(message)))