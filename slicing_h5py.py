import h5py

filename = 'mock_febus_data.h5'

with h5py.File(filename, 'r') as f:
    # Acessando o Dataset de temperatura, mas NÃO o carregando na memória ainda
    temp_dataset = f['extractedTemperature']

    # Medindo as propriedades do dataset SEM carregar na memória
    print(f"--- Medindo o Dataset ---")
    print(f"Formato (Shape): {temp_dataset.shape}")
    print(f"Total de elementos: {temp_dataset.size}")
    print(f"Tipo de dado: {temp_dataset.dtype}")
    
    # Calculando o tamanho em Megabytes (MB)
    tamanho_mb = (temp_dataset.size * temp_dataset.dtype.itemsize) / (1024 * 1024)
    print(f"Tamanho na memória: {tamanho_mb:.4f} MB")
    print(f"-------------------------\n")

    
    print(f"Formato total do Dataset na leitura: {temp_dataset.shape}")
    
    # FATIAMENTO (Slicing): Trazendo para a RAM apenas os dados
    # das 5 primeiras medições (índices 0 a 5) da posição 450m a 550m
    # (aquela onde você simulou o Hot Spot!)
    hot_spot_chunk = temp_dataset[0:5, 450:550]
    
    print(f"\nFormato do dado carregado na memória: {hot_spot_chunk.shape}")
    print(f"Temperatura média no Hot Spot nas primeiras medições: {hot_spot_chunk.mean():.2f} °C")
