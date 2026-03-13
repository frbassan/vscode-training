import h5py
import matplotlib.pyplot as plt

with h5py.File('mock_febus_data.h5', 'r') as f:
    temp_matrix = f['extractedTemperature'][:]
    dist = f['distances'][:]
    
    # Plotting the last measurement in time
    plt.plot(dist, temp_matrix[-1, :])
    plt.title("Temperature Profile along the Fiber")
    plt.xlabel("Distance (m)")
    plt.ylabel("Temperature (°C)")
    plt.show()