import h5py

def extract_all(file_path):
    def scan_item(name, obj):
        # 1. Define indentation based on depth level
        indent = "  " * name.count('/')
        
        # 2. Identify object type
        if isinstance(obj, h5py.Group):
            print(f"{indent}📁 Group: {name}")
        elif isinstance(obj, h5py.Dataset):
            print(f"{indent}📊 Dataset: {name}")
            print(f"{indent}   Type: {obj.dtype} | Shape: {obj.shape}")

        # 3. Extract and list Metadata (Attributes) of this object
        if len(obj.attrs) > 0:
            for attr_name, attr_value in obj.attrs.items():
                # Decode if binary (common in sensor files)
                if isinstance(attr_value, bytes):
                    attr_value = attr_value.decode('utf-8', errors='ignore')
                print(f"{indent}   🏷️ Attribute [{attr_name}]: {attr_value}")

    with h5py.File(file_path, 'r') as f:
        print(f"=== FULL EXTRACTION: {file_path} ===\n")
        
        # 4. List root metadata ('/') - visititems skips the root
        print("🌍 [Root /]")
        for r_name, r_val in f.attrs.items():
            if isinstance(r_val, bytes): r_val = r_val.decode('utf-8')
            print(f"   🏷️ {r_name}: {r_val}")
        
        print("\n" + "-"*50 + "\n")

        # 5. Recursively iterate through all items
        f.visititems(scan_item)

# Testing with the synthetic file
extract_all('mock_febus_data.h5')