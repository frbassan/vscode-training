import h5py

def show_metadata(file_path):
    with h5py.File(file_path, 'r') as f:
        print(f"--- EXPLORING METADATA FROM: {file_path} ---\n")

        # 1. Global Metadata (at the root of the file)
        print("🌍 [Global/Root Metadata]")
        if len(f.attrs) > 0:
            for key, val in f.attrs.items():
                print(f"   🏷️ {key}: {val}")
        else:
            print("   (No global metadata found)")

        print("\n" + "-"*40 + "\n")

        # 2. Metadata for each specific Dataset
        print("📊 [Metadata per Dataset]")
        
        def find_attrs(name, obj):
            if len(obj.attrs) > 0:
                print(f"\n📍 In item: {name}")
                for key, val in obj.attrs.items():
                    # Decode strings if necessary (common in HDF5)
                    if isinstance(val, bytes):
                        val = val.decode('utf-8')
                    print(f"   🏷️ {key}: {val}")

        f.visititems(find_attrs)

# Run for the synthetic file we generated
show_metadata('mock_febus_data.h5')