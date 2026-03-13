import h5py

def print_structure(name, obj):
    """
    Callback function called by h5py for each item in the file.
    """
    # Calculates indentation based on depth level (counting '/' slashes)
    indent = "    " * name.count('/')
    
    # Checks if the item is a Group (like a folder)
    if isinstance(obj, h5py.Group):
        print(f"{indent}📁 Group: {name}")
    
    # Checks if the item is a Dataset (like a spreadsheet/matrix)
    elif isinstance(obj, h5py.Dataset):
        print(f"{indent}📊 Dataset: {name} | Shape: {obj.shape} | Type: {obj.dtype}")

    # Lists Attributes (metadata) associated with this item, if any
    for attr_name, attr_value in obj.attrs.items():
        print(f"{indent}    🏷️ Attribute: {attr_name} = {attr_value}")

# Name of the file you want to explore
file_name = 'mock_febus_data.h5' 

try:
    with h5py.File(file_name, 'r') as f:
        print(f"Hierarchical File Structure: {file_name}\n")
        # visititems iterates over each object and calls print_structure
        f.visititems(print_structure)
except FileNotFoundError:
    print(f"Error: File '{file_name}' not found.")
except Exception as e:
    print(f"An error occurred while reading the file: {e}")