import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# SIMULAÇÃO 2: A Matemática do Sintonizador DDC (Digital Down-Converter)
# =====================================================================
# Objetivo: Mostrar como a FEBUS filtra o ruído de um pulso de luz e 
# escuta apenas a energia de UM único tom (ex: 330 MHz).
# Isso mantém a resolução óptica perfeitamente intacta.
# =====================================================================

print("--- Iniciando Simulação do Sintonizador DDC (A Verdadeira) ---")

taxa_amostragem_adc = 1e9  # 1 GS/s
tamanho_fibra = 8500 # 8500 ns (equivale aos 850m de fibra na sua amostragem de 0.1m)

tempo = np.arange(tamanho_fibra) / taxa_amostragem_adc 

# 1. Novamente o Eco vindo da fibra daquele pulso (Onda de rádio em 330 MHz p/ a luz inteira)
freq_real_pulso = 330.0e6
sinal_adc = np.cos(2 * np.pi * freq_real_pulso * tempo)
sinal_adc += np.random.normal(0, 0.5, tamanho_fibra)  # Ruído elétrico constante da máquina

print("\nA máquina atirou O PRIMEIRO pulso gerando 8500 leituras analógicas contínuas.")

# Para adicionar realismo físico: vamos simular um "Ponto Quente" (Hotspot) ali pelo Metro 400
# Onde a onda brilhante do sinal responde com muito mais força.
sinal_adc[4000:4100] *= 2.5 

# 2. O SINTONIZADOR (Oscilador Controlado Numericamente - NCO)
# A placa mãe configura o "Dial RF" virando para os 330.0 MHz exatos
frequencia_sintonizador = 330.0e6 
print(f"O FPGA sintoniza os canais de hardware para o alvo: {frequencia_sintonizador/1e6:.2f} MHz")

# Matemática de Demodulação contínua do FPGA (A tabuada das trigonométricas gerada na placa)
# Ele gera as réguas para a fibra inteira simultaneamente:
nco_cos_I = np.cos(2 * np.pi * frequencia_sintonizador * tempo)
nco_sin_Q = np.sin(2 * np.pi * frequencia_sintonizador * tempo)

# O MISTURADOR DIGITAL (Mixagem do vetor inteiro velozmente)
mix_I = sinal_adc * nco_cos_I
mix_Q = sinal_adc * nco_sin_Q

# O FILTRO PASSA-BAIXA DIGITAL (A preservação do espaço)
# Ao invés de moer a onda toda num FFT ou em 1 média total...
# O FPGA aplica um Filtro de Média Móvel (ex: janela deslizante de 50 ns no hardware).
# Isso mata o ruído agudo, MAS CONSERVA O DIMENSIONAMENTO de 8500 casinhas!
comprimento_filtro = 50
janela_filtro = np.ones(comprimento_filtro) / comprimento_filtro

# Convolução (Média Móvel Deslizante Rápida do FPGA)
energia_I = np.convolve(mix_I, janela_filtro, mode='same')
energia_Q = np.convolve(mix_Q, janela_filtro, mode='same')

# A Amplitude limpa daquele Pulso resultando em UM traço espacial da matriz (8500 distância, 1 freq)
amplitude_limpa = np.sqrt(energia_I**2 + energia_Q**2)

print("-> Pulso 1 Processado! Ele cuspiu 1 coluna perfeita de 8500 amostras puras!")
print("-> O Loop de Hardware começaria o Pulso 2 alterando o Sintonizador para 331.95 MHz...")

# ================= Visualização (A Linha da Fibra) ================= #
plt.figure(figsize=(12, 8))

# Subplot 1: Domínio do Tempo original da Fibra Inteira
plt.subplot(2, 1, 1)
plt.plot(tempo * 1e9, sinal_adc, color='blue', alpha=0.5)
plt.title("Sinal Bruto Pós-Fotodiodo (8500 pontos, engolido a 1 GSa/s)")
plt.xlabel("Tempo (Variável de Propagação Espacial da Fibra)")
plt.ylabel("Voltagem")
plt.grid(True)

# Subplot 2: Resultado Espacial Deslizado
plt.subplot(2, 1, 2)
plt.plot(tempo * 1e9, amplitude_limpa, label=f'Camada Brilhante da Matriz ({frequencia_sintonizador/1e6:.1f} MHz)', color='green', linewidth=2)
plt.title("Saída Magistral do Filtro FPGA (As 8500 amostras perfeititas prontas pra Matriz MTX)")
plt.xlabel("Tempo (ns) ==> Distância Físico-Espacial (metros)")
plt.ylabel("Energia Acústica do Brillouin")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()
