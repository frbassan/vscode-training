import h5py
import numpy as np
import time

# Nome do arquivo de saída
filename = "mock_febus_data.h5"

# Configurações da simulação
num_points = 1000  # 1km de fibra com resolução de 1m
num_measures = 50  # 50 aquisições ao longo do tempo

# 1. Criando eixos de distância e tempo
distances = np.linspace(0, 1000, num_points)
start_times = np.linspace(0, 3600, num_measures) # 1 hora de dados
end_times = start_times + 2 # Cada medição dura 2s

# 2. Gerando dados de temperatura (Base de 25°C + Ruído)
temp_data = 25 + np.random.normal(0, 0.2, (num_measures, num_points))

# Adicionando um "Hot Spot" (Aquecimento entre os metros 450 e 550)
temp_data[:, 450:550] += 15.0  

# 3. Gerando dados de deformação (Base 0 + Ruído)
strain_data = np.random.normal(0, 5, (num_measures, num_points))

# Adicionando um "Strain Point" (Tração entre os metros 200 e 250)
strain_data[:, 200:250] += 150.0 

# 4. Criando o arquivo HDF5 com a estrutura do manual
with h5py.File(filename, 'w') as f:
    # Criando os datasets principais (usando os nomes do manual)
    f.create_dataset("distances", data=distances)
    f.create_dataset("start_times", data=start_times)
    f.create_dataset("end_times", data=end_times)
    f.create_dataset("extractedTemperature", data=temp_data)
    f.create_dataset("extractedDeformation", data=strain_data)
    
    # Adicionando alguns metadados de exemplo
    f.attrs['interrogator_model'] = "FEBUS G2-R"
    f.attrs['location'] = "California Test Site"
    f.attrs['pulse_width_ns'] = 50

print(f"Arquivo '{filename}' gerado com sucesso!")