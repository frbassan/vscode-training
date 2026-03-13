import h5py
import matplotlib.pyplot as plt

with h5py.File('mock_febus_data.h5', 'r') as f:
    temp_matrix = f['extractedTemperature'][:]
    dist = f['distances'][:]
    
    # Plotando a última medição no tempo
    plt.plot(dist, temp_matrix[-1, :])
    plt.title("Perfil de Temperatura ao longo da Fibra")
    plt.xlabel("Distância (m)")
    plt.ylabel("Temperatura (°C)")
    plt.show()