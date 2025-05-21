import time
import secrets  # For cryptographically secure random numbers
import threading # For thread-safety in the stateful generator

from uuid7 import generator, UUIDv7

if __name__ == '__main__':
    generator = UUIDv7()

    print("Generating some UUIDv7 identifiers from scratch:")
    uuids = []
    for i in range(5):
        uid = generator.generate()
        uuids.append(uid)
        print(f"[{i+1}] {uid}")
        if i < 4: # Add a tiny delay to increase chance of different ms for initial test
            time.sleep(0.0011)


    print("\nVerifying sortability (should be time-ordered):")
    # Sort the generated UUIDs
    uuids_sorted_lexicographically = sorted(uuids)

    if uuids == uuids_sorted_lexicographically:
        print("UUIDs were generated in lexicographically sortable order.")
    else:
        print("UUIDs were NOT generated in lexicographically sortable order.")
        print("Original:", uuids)
        print("Sorted:  ", uuids_sorted_lexicographically)

    print("\nGenerating 10,000 UUIDs quickly to test monotonicity & performance:")
    # Increased number for better stress testing
    num_quick_uuids = 10000
    quick_uuids = [generator.generate() for _ in range(num_quick_uuids)]
    
    is_monotonic = True
    first_non_monotonic_pair = None
    for i in range(len(quick_uuids)-1):
        if not (quick_uuids[i] < quick_uuids[i+1]):
            is_monotonic = False
            first_non_monotonic_pair = (quick_uuids[i], quick_uuids[i+1], i)
            break
            
    if is_monotonic:
        print(f"{num_quick_uuids} UUIDs generated quickly are strictly monotonic.")
    else:
        print(f"ERROR: {num_quick_uuids} UUIDs generated quickly are NOT strictly monotonic.")
        if first_non_monotonic_pair:
            print(f"First non-monotonic pair: {first_non_monotonic_pair[0]} (index {first_non_monotonic_pair[2]}) and {first_non_monotonic_pair[1]} (index {first_non_monotonic_pair[2]+1})")
    
    # Example of how the timestamp is encoded
    if quick_uuids:
        test_uuid = quick_uuids[0]
        print(f"\nExample UUID: {test_uuid}")
        try:
            uuid_bytes_val = bytes.fromhex(test_uuid.replace('-', ''))
            # Timestamp is the first 6 bytes (48 bits)
            timestamp_from_uuid = int.from_bytes(uuid_bytes_val[0:6], 'big')
            # rand_a is next 12 bits, so after 48 bits (6 bytes), it's part of byte 6 and byte 7
            # Version is 4 bits (bits 48-51)
            # rand_a is 12 bits (bits 52-63)
            # Byte 6: TTTT VVVV (T=timestamp, V=version)
            # Byte 7: RRRR RRRR (R=rand_a)
            # Byte 8: RRRR XXXX (R=rand_a, X=variant and start of rand_b)
            
            # Extracting rand_a from bytes:
            # rand_a_ver_chunk = int.from_bytes(uuid_bytes_val[6:8], 'big') # Gets bytes 6 and 7
            # rand_a_val = (rand_a_ver_chunk & 0x0FFF0) >> 4 # This is tricky due to byte alignment
            # A simpler way to verify is to decode the full int and mask
            full_int = int.from_bytes(uuid_bytes_val, 'big')
            rand_a_from_uuid = (full_int >> 64) & 0xFFF # 0xFFF is 12 bits set to 1

            print(f"Timestamp from UUID (ms): {timestamp_from_uuid}")
            print(f"rand_a from UUID (hex):   {rand_a_from_uuid:03x}") # 03x ensures 3 hex digits
            print(f"Current generator's _last_ts (ms): {generator._last_ts}")
            print(f"Current generator's _last_rand_a (hex): {generator._last_rand_a:03x}")
        except ValueError:
            print("Could not parse example UUID for detailed info.")

