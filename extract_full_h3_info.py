import h5py

def extract_all(file_path):
    def scan_item(name, obj):
        # 1. Definir a indentação por nível de profundidade
        indent = "  " * name.count('/')
        
        # 2. Identificar o tipo de objeto
        if isinstance(obj, h5py.Group):
            print(f"{indent}📁 Grupo: {name}")
        elif isinstance(obj, h5py.Dataset):
            print(f"{indent}📊 Dataset: {name}")
            print(f"{indent}   Type: {obj.dtype} | Shape: {obj.shape}")

        # 3. Extrair e listar Metadados (Atributos) deste objeto
        if len(obj.attrs) > 0:
            for attr_name, attr_value in obj.attrs.items():
                # Decodificar se for binário (comum em arquivos de sensores)
                if isinstance(attr_value, bytes):
                    attr_value = attr_value.decode('utf-8', errors='ignore')
                print(f"{indent}   🏷️ Atributo [{attr_name}]: {attr_value}")

    with h5py.File(file_path, 'r') as f:
        print(f"=== EXTRAÇÃO COMPLETA: {file_path} ===\n")
        
        # 4. Listar metadados da Raiz (Root '/') - O visititems pula a raiz
        print("🌍 [Raiz /]")
        for r_name, r_val in f.attrs.items():
            if isinstance(r_val, bytes): r_val = r_val.decode('utf-8')
            print(f"   🏷️ {r_name}: {r_val}")
        
        print("\n" + "-"*50 + "\n")

        # 5. Percorrer recursivamente todos os itens
        f.visititems(scan_item)

# Testando com o arquivo sintético (ou o que o Qing enviar)
extract_all('mock_febus_data.h5')