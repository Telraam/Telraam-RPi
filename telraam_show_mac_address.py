import uuid


def quad_insert_hyphens(s):
    return '-'.join(s[i:i+4] for i in range(0, len(s), 4))


mac_addr_dec = str(uuid.getnode())
mac_addr_hex = str(hex(uuid.getnode()).replace('0x',''))

print("Hexadecimal MAC address: " + quad_insert_hyphens(mac_addr_hex))
print("Decimal MAC address    : " + quad_insert_hyphens(mac_addr_dec))
