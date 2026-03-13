import h5py

def print_structure(name, obj):
    """
    Função de callback que o h5py chama para cada item no arquivo.
    """
    # Calcula a indentação baseada no nível de profundidade (contando as barras '/')
    indent = "    " * name.count('/')
    
    # Verifica se o item é um Grupo (como uma pasta)
    if isinstance(obj, h5py.Group):
        print(f"{indent}📁 Grupo: {name}")
    
    # Verifica se o item é um Dataset (como uma planilha/matriz)
    elif isinstance(obj, h5py.Dataset):
        print(f"{indent}📊 Dataset: {name} | Shape: {obj.shape} | Tipo: {obj.dtype}")

    # Lista os Atributos (metadados) associados a este item, se existirem
    for attr_name, attr_value in obj.attrs.items():
        print(f"{indent}    🏷️ Atributo: {attr_name} = {attr_value}")

# Nome do arquivo que você deseja explorar
nome_do_arquivo = 'mock_febus_data.h5' 

try:
    with h5py.File(nome_do_arquivo, 'r') as f:
        print(f"Estrutura Hierárquica do Arquivo: {nome_do_arquivo}\n")
        # O visititems percorre cada objeto e chama a função print_structure
        f.visititems(print_structure)
except FileNotFoundError:
    print(f"Erro: O arquivo '{nome_do_arquivo}' não foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro ao ler o arquivo: {e}")