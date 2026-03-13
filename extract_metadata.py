import h5py

def show_metadata(file_path):
    with h5py.File(file_path, 'r') as f:
        print(f"--- EXPLORANDO METADADOS DE: {file_path} ---\n")

        # 1. Metadados Globais (na raiz do arquivo)
        print("🌍 [Metadados Globais/Raiz]")
        if len(f.attrs) > 0:
            for key, val in f.attrs.items():
                print(f"   🏷️ {key}: {val}")
        else:
            print("   (Nenhum metadado global encontrado)")

        print("\n" + "-"*40 + "\n")

        # 2. Metadados de cada Dataset específico
        print("📊 [Metadados por Dataset]")
        
        def find_attrs(name, obj):
            if len(obj.attrs) > 0:
                print(f"\n📍 No item: {name}")
                for key, val in obj.attrs.items():
                    # Decodifica strings se necessário (comum em HDF5)
                    if isinstance(val, bytes):
                        val = val.decode('utf-8')
                    print(f"   🏷️ {key}: {val}")

        f.visititems(find_attrs)

# Executa para o arquivo sintético que geramos
show_metadata('mock_febus_data.h5')