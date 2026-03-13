import h5py
import numpy as np
import time

# Output filename
filename = "mock_febus_data.h5"

# Simulation settings
num_points = 1000  # 1km of fiber with 1m resolution
num_measures = 50  # 50 acquisitions over time

# 1. Creating distance and time axes
distances = np.linspace(0, 1000, num_points)
start_times = np.linspace(0, 3600, num_measures) # 1 hour of data
end_times = start_times + 2 # Each measurement lasts 2s

# 2. Generating temperature data (Base 25°C + Noise)
temp_data = 25 + np.random.normal(0, 0.2, (num_measures, num_points))

# Adding a "Hot Spot" (Heating between meters 450 and 550)
temp_data[:, 450:550] += 15.0  

# 3. Generating strain data (Base 0 + Noise)
strain_data = np.random.normal(0, 5, (num_measures, num_points))

# Adding a "Strain Point" (Traction between meters 200 and 250)
strain_data[:, 200:250] += 150.0 

# 4. Creating the HDF5 file with the manual structure
with h5py.File(filename, 'w') as f:
    # Creating the main datasets (using names from the manual)
    f.create_dataset("distances", data=distances)
    f.create_dataset("start_times", data=start_times)
    f.create_dataset("end_times", data=end_times)
    f.create_dataset("extractedTemperature", data=temp_data)
    f.create_dataset("extractedDeformation", data=strain_data)
    
    # Adding some example metadata
    f.attrs['interrogator_model'] = "FEBUS G2-R"
    f.attrs['location'] = "California Test Site"
    f.attrs['pulse_width_ns'] = 50

print(f"File '{filename}' generated successfully!")