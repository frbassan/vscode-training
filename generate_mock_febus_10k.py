import h5py
import numpy as np
import time

# --- Configurações da Simulação ---
filename = "mock_febus_data_10k.h5"
num_points = 10000    # 10km de fibra com resolução de 1m
num_measures = 1000   # 1000 aquisições
pulse_width_ns = 10   # 10ns = 1m de resolução

# --- Relação Sinal-Ruído (SNR) ---
# Valores menores = MAIS ruído (sinal mais sujo). Valores maiores = MENOS ruído.

# 1. Criando eixos de distância
distances = np.linspace(0, 10000, num_points)

# ----------------------------------------------------
# 2. Gerando Temperatura (Base 25°C + Ruído pesado)
# ----------------------------------------------------
base_temp = 25.0
noise_amplitude_temp = 5
temp_data = base_temp + np.random.normal(0, noise_amplitude_temp, (num_measures, num_points))

# Injetando 5 Zonas de Temperatura Elevada (Hot Spots) com larguras e intensidades variadas
hotspots = [
    {"start": 1000, "end": 1050, "intensity": -8.0},   # Snow
    {"start": 3200, "end": 3300, "intensity": 45.0},   # Vazamento crítico
    {"start": 4200, "end": 4250, "intensity": 25.0},   # Fogo em vegetação próxima
    {"start": 5500, "end": 5520, "intensity": 15.0},   # Ponto quente na emenda
    {"start": 7800, "end": 8000, "intensity": 5.0},    # Aquecimento solar em trecho exposto
    {"start": 9100, "end": 9105, "intensity": 60.0}    # Curto-circuito pontual altíssimo
]

for hs in hotspots:
    # Adicionando o hotspot com intensidade estática em todo o bloco de tempo
    temp_data[:, hs["start"]:hs["end"]] += hs["intensity"]

# ----------------------------------------------------
# 3. Gerando Strain (Base 0 + Ruído pesado)
# ----------------------------------------------------
base_strain = 0.0
noise_amplitude_strain = 100.0
strain_data = base_strain + np.random.normal(0, noise_amplitude_strain, (num_measures, num_points))

# Injetando 5 Zonas de Strain Elevado (Tração/Compressão)
strain_spots = [
    {"start": 500, "end": 600, "intensity": 350.0},     # Assentamento de solo
    {"start": 2500, "end": 2550, "intensity": -150.0},  # Compressão
    {"start": 4800, "end": 4850, "intensity": 800.0},   # Trinca se abrindo subitamente
    {"start": 6200, "end": 6300, "intensity": 400.0},   # Deslizamento de terra tensionando cabo
    {"start": 8500, "end": 8550, "intensity": -300.0}   # Compressão forte
]

for ss in strain_spots:
    # Evento de strain com intensidade estática no espaço e no tempo (bloco retangular)
    strain_data[:, ss["start"]:ss["end"]] += ss["intensity"]


# ----------------------------------------------------
# 4. Criando o arquivo HDF5
# ----------------------------------------------------
with h5py.File(filename, 'w') as f:
    f.create_dataset("distances", data=distances)

    
    # Chunking ativado para otimizar leitura do Slice no Streamlit para arquivos grandes
    f.create_dataset("extractedTemperature", data=temp_data, chunks=(1, num_points), compression="gzip")
    f.create_dataset("extractedDeformation", data=strain_data, chunks=(1, num_points), compression="gzip")
    
    f.attrs['interrogator_model'] = "FEBUS G2-R"
    f.attrs['location'] = "TS Conductor Mega Test Site"
    f.attrs['pulse_width_ns'] = float(pulse_width_ns)
    f.attrs['noise_temp_amplitude_°C'] = float(noise_amplitude_temp)
    f.attrs['noise_strain_amplitude_µε'] = float(noise_amplitude_strain)

print(f"Arquivo '{filename}' (10.000 pontos) gerado com sucesso!")
