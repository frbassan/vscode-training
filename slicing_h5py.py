import h5py

filename = 'mock_febus_data.h5'

with h5py.File(filename, 'r') as f:
    # Accessing the temperature dataset, but NOT loading it into memory yet
    temp_dataset = f['extractedTemperature']

    # Measuring dataset properties WITHOUT loading it into memory
    print(f"--- Measuring the Dataset ---")
    print(f"Shape: {temp_dataset.shape}")
    print(f"Total elements: {temp_dataset.size}")
    print(f"Data type: {temp_dataset.dtype}")
    
    # Calculating size in Megabytes (MB)
    tamanho_mb = (temp_dataset.size * temp_dataset.dtype.itemsize) / (1024 * 1024)
    print(f"Size in memory: {tamanho_mb:.4f} MB")
    print(f"-------------------------\n")

    
    print(f"Total shape of the Dataset on read: {temp_dataset.shape}")
    
    # SLICING: Bringing to RAM only the data
    # of the first 5 measurements (indices 0 to 5) from position 450m to 550m
    # (where the Hot Spot was simulated!)
    hot_spot_chunk = temp_dataset[0:5, 450:550]
    
    print(f"\nShape of the data loaded into memory: {hot_spot_chunk.shape}")
    print(f"Average temperature in the Hot Spot in the first measurements: {hot_spot_chunk.mean():.2f} °C")
