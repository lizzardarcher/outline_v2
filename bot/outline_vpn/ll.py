from outline_vpn.outline_vpn import OutlineVPN

# Setup the access with the API URL (Use the one provided to you after the server setup)
client = OutlineVPN(api_url="https://185.68.22.164:5224/HnGwms6u2fHOmd2UeALRXg",
                    cert_sha256="e6652ac3-b222-4f16-b236-4ab62d9be284")
'''
{"apiUrl":"https://5.165.21.226:48988/ODDb3cG2oWtd8Ur79qTFoQ","certSha256":"820FD4D43FBFC1D6DEDFED6B0B8D4D934E1A3D0636E6C9BAEE163E0EEDCE7634"}

'''
# Get all access URLs on the server
for key in client.get_keys():
    print(key.access_url)

# Create a new key
new_key = client.create_key()
print(new_key)
# Rename it
# client.rename_key(new_key.key_id, "new_key")

# Delete it
# client.delete_key(new_key.key_id)

# Set a monthly data limit for a key (20MB)
# client.add_data_limit(new_key.key_id, 1000 * 1000 * 20)

# Remove the data limit
# client.delete_data_limit(new_key.key_id)