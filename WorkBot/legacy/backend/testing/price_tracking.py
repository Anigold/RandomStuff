import re

def parse_pack_size(description):
    """
    Parses a pack-size description and extracts its constituent parts.
    
    - Supports formats like: "6/5 LB", "10 LB", "24/8 OZ", "36 EA"
    - Handles ranged weights like "1/10-15 LB" (averages to 12.5 LB)
    - Ignores multi-level pack sizes (e.g., "2/20/4 OZ")
    - Keeps units unchanged
    """
    
    # Regular expression to match standard and ranged pack sizes
    pattern = re.compile(r'(?:(\d+)/)?(\d+)(?:-(\d+))?\s*([a-z#]+)', re.IGNORECASE)
    match = pattern.fullmatch(description.strip())

    if not match:
        return None  # Return None if the format is unrecognized

    packs_per_case = match.group(1)  # Number of packs per case (optional)
    min_size       = match.group(2)        # Minimum pack size
    max_size       = match.group(3)        # Maximum pack size (if range is present)
    unit           = match.group(4).upper()    # Unit of measurement (LB, OZ, EA, etc.)

    # Convert extracted values
    packs_per_case = int(packs_per_case) if packs_per_case else 1
    min_size = float(min_size)

    # If there's a max size, calculate the average
    size_per_pack = (
        round((min_size + float(max_size)) / 2, 2) if max_size else min_size
    )

    return {
        "packs_per_case": packs_per_case,
        "size_per_pack": size_per_pack,
        "unit": unit
    }

# Example test cases
test_descriptions = [
    "6/10 OZ",        # Standard format
    "24/8 OZ",        # Standard format
    "5 LB",           # Single pack
    "36 EA",          # Single pack
    "4/2.5 LB",       # Standard format
    "1/10-15 LB",     # Ranged weight → 1 pack of 12.5 LB
    "4/20-30 EA",     # Ranged count → 4 packs of 25 EA
    "2/20/4 OZ",      # Multi-level (ignored)
]

# Run test cases
for desc in test_descriptions:
    print(f"{desc} -> {parse_pack_size(desc)}")
