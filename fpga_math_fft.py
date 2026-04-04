import numpy as np
import matplotlib.pyplot as plt

# =====================================================================
# SIMULAÇÃO 1: A Matemática da Transformada de Fourier (FFT) no FPGA
# =====================================================================
# Objetivo: Mostrar como um bloco de FFT processa um bloco de tempo,
# extraindo todas as frequências DE UMA ÚNICA VEZ.
# =====================================================================

print("--- Iniciando Simulação de FFT ---")

# 1. Configurando o "ADC Virtual"
taxa_amostragem_adc = 1e9  # 1 GS/s (1 Bilhão de amostras por segundo)
tamanho_bloco_fft = 512    # Tamanho mínimo de pacotes que a FFT exige

# Vetor de tempo discreto para as 512 amostras (512 ns de duração total)
tempo = np.arange(tamanho_bloco_fft) / taxa_amostragem_adc 

# 2. Criando o Sinal Falso da Fibra Óptica (Sinal Misturado Sujo)
# Vamos fingir que o nosso "batimento" atual está ressoando em 330 MHz
freq_sinal_real = 330.0e6  # 330 MHz

# O sinal detectado pelo Fotodiodo (uma onda Cosseno + Chiado térmico)
sinal_adc = np.cos(2 * np.pi * freq_sinal_real * tempo) 
ruido = np.random.normal(0, 0.5, tamanho_bloco_fft)
sinal_adc += ruido # O sinal de entrada que o FPGA enxerga

# 3. A Matemática Mágica do FPGA (A Transformada de Fourier Radix-2)
# No FPGA, a FFT não roda instrução por instrução. Ela usa múltiplos
# multiplicadores cruzados (Borboletas Radix-2) disparando ao mesmo tempo.
print("Calculando FFT de 512 pontos...")
espectro_complexo = np.fft.fft(sinal_adc)

# A FFT gera números imaginários. O FPGA precisa calcular o "Módulo" (Amplitude)
# Amplitude = Raiz(Real^2 + Imaginário^2)
amplitudes = np.abs(espectro_complexo) / tamanho_bloco_fft * 2

# O ADC amostra 1 GHz, então as bandas de frequência criadas vão de 0 a 1 GHz.
frequencias_geradas = np.fft.fftfreq(tamanho_bloco_fft, d=1/taxa_amostragem_adc)

# No FPGA, só a primeira metade das bandas (frequências positivas) importa.
metade = tamanho_bloco_fft // 2
frequencias_positivas = frequencias_geradas[:metade]
amplitudes_positivas = amplitudes[:metade]

# Encontrando a "Caixinha" que brilhou mais forte
indice_pico = np.argmax(amplitudes_positivas)
freq_pico = frequencias_positivas[indice_pico]
amp_pico = amplitudes_positivas[indice_pico]

print(f"Resolução da 'Caixinha' de Frequência: {taxa_amostragem_adc/tamanho_bloco_fft / 1e6:.6f} MHz")
print(f"Pico Encontrado: {freq_pico/1e6:.2f} MHz com amplitude {amp_pico:.2f}")

# Plot para entender visualmente
plt.figure(figsize=(10, 8))

# Subplot 1: Domínio do Tempo
plt.subplot(2, 1, 1)
plt.plot(tempo * 1e9, sinal_adc, color='blue', alpha=0.7)
plt.title("Sinal no Domínio do Tempo (Direto do Fotodiodo)")
plt.xlabel("Tempo (ns)")
plt.ylabel("Voltagem (Amplitude Bruta)")
plt.grid(True)

# Subplot 2: Domínio da Frequência
plt.subplot(2, 1, 2)
plt.plot(frequencias_positivas / 1e6, amplitudes_positivas, color='purple')
plt.axvline(freq_pico/1e6, color='red', linestyle='--', label=f"Pico: {freq_pico/1e6:.2f} MHz")
plt.title("Onda quebrada em 256 'Caixinhas' (Frequências Múltiplas) num Tiro Só")
plt.xlabel("Frequências Detectadas (MHz)")
plt.ylabel("Amplitude")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

print("\nConclusão da FFT:")
print("A matemática expôs a presença de TODOS os tons simultaneamente.")
print("Problema na fibra: O FPGA precisou consumir e esmagar 512 ns (51 metros físicos) do\ntempo espacial só para montar UMA foto de várias frequências, estragando\na resolução óptica de 0.1m.")
