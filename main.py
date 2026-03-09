import pandas as pd
import json
import re
import os
from tqdm import tqdm

# Initialize tqdm for Pandas integration
tqdm.pandas()


def load_config(file_path):
    """Load configuration and mapping data from a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def clean_address_pro(raw_address, config):
    # 1. STANDARDIZATION & SYMBOL CLEANUP
    text = str(raw_address).upper()

    # Smart Logic: Convert "/" to "RW" ONLY if it follows "RT"
    # Example: RT 05/01 -> RT 05 RW 01
    # Example: C6/12 -> C6/12 (will be converted to NOMOR later)
    text = re.sub(r'(RT\s*\d+)[\\/](\d+)', r'\1 RW \2', text)

    # Convert all other slashes (like in house numbers or blocks) into 'NOMOR'
    text = text.replace("\\/", " NOMOR ").replace("/", " NOMOR ").replace(".", " ")

    # 2. BASIC MAPPING (Roads, Sub-districts, Districts)
    basic_maps = {
        "JL": "JALAN", "JLN": "JALAN", "KAV": "KAVLING",
        "NO": "NOMOR", "KM": "KM", "GG": "GANG",
        "KEC": "KECAMATAN", "KEL": "KELURAHAN",
        "DEPN":"DEPAN", "JEND":"JENDERAL"
    }
    for short, full in basic_maps.items():
        text = re.sub(rf'\b{short}\b', full, text)

    found_city, found_prov = "-", "-"
    city_list = config['cities']
    all_mappings = config['mappings']

    # 3. GEOGRAPHICAL EXTRACTION (Backward Priority Logic)
    search_keys = []
    for city in city_list.keys():
        search_keys.append((city, city))
    for short, full in all_mappings.items():
        if full in city_list:
            search_keys.append((short, full))

    # Sort keys by length (descending) to prevent partial matching
    search_keys.sort(key=lambda x: len(x[0]), reverse=True)

    best_pos = -1
    matched_key = None
    for key, full_name in search_keys:
        matches = list(re.finditer(rf'\b{key}\b', text))
        if matches:
            last_match = matches[-1]
            if last_match.start() > best_pos:
                best_pos = last_match.start()
                found_city = full_name
                found_prov = city_list[full_name]
                matched_key = key

    # 4. DATA SANITIZATION (Remove identified city/province from street address)
    if found_city != "-":
        text = re.sub(rf'\b{matched_key}\b', "", text)
        text = text.replace(found_city, "").replace(found_prov, "")

    # Remove residual province abbreviations (e.g., JABAR, DKI)
    all_provinces = set(city_list.values())
    prov_shorts = [k for k, v in all_mappings.items() if v in all_provinces or k in all_provinces]
    trash_words = list(all_provinces) + prov_shorts + ["DKI", "PROVINSI"]

    for word in trash_words:
        text = re.sub(rf'\b{word}\b', "", text)

    # 5. FINAL FORMATTING (Visual Polish)
    street = re.sub(r'[, ]+$', '', text)
    street = re.sub(r'\s+', ' ', street).strip(", ").title()

    # CUSTOM FIXES (Ensure RT/RW/SR and Roman numerals remain uppercase)
    special_fixes = {
        "Rt": "RT ", "Rw": "RW ", "Km": "KM ",
        "Iii": "III", "Ii": "II", "Iv": "IV",
        "Sr": "SR", "Bi": "BI", "Gg": "GG",
        "Kavling": "Kavling"
    }

    for wrong, right in special_fixes.items():
        street = street.replace(wrong, right)

    # Final cleanup of any potential double spaces
    street = re.sub(r'\s+', ' ', street).strip()

    final_city = found_city.title()
    final_prov = found_prov.title().replace("Dki", "DKI")

    return pd.Series([street, final_city, final_prov])


def main():
    print("\n" + "=" * 50)
    print("🚀 ADDRESS CLEANER - 1.0")
    print("Mini Project RH")
    print("=" * 50)

    # Load configuration files
    config = load_config('references.json')
    if not os.path.exists('raw_address.json'):
        print("❌ Error: 'raw_address.json' not found in current directory.")
        return

    # Load Source Data
    df = pd.read_json('raw_address.json')
    print(f"📦 Total Records Loaded: {len(df)}")

    # Execute cleaning with Progress Bar
    print("🔄 Standardizing addresses and mapping regions...")
    df[['street_address', 'city', 'province']] = df['raw_address'].progress_apply(
        lambda x: clean_address_pro(x, config)
    )

    # Export to JSON
    output_file = 'clean_address.json'
    df.to_json(output_file, orient='records', indent=4)

    print("\n" + "-" * 50)
    print("✅ PROCESS COMPLETED SUCCESSFULLY!")
    print(f"📁 Output saved to: {os.path.abspath(output_file)}")
    print("-" * 50)


if __name__ == "__main__":
    main()