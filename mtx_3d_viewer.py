import streamlit as st
import h5py
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(page_title="MTX 3D Viewer", layout="wide")
st.title("BOTDA BGS Matrix Viewer 📉")
st.markdown("Visualização Avançada em Mapa de Calor e 3D para Matrizes Acústicas e Ópticas.")

st.sidebar.header("Arquivo de Matriz MTX")
file_path = st.sidebar.text_input("Caminho do Arquivo .h5:", value="FiberTest_10sec_C1_2026-04-02T15.16.11-0700.mtx.h5")

if 'file_path' not in st.session_state:
    st.session_state['file_path'] = file_path

if st.sidebar.button("Carregar Arquivo"):
    st.session_state['file_path'] = file_path

try:
    if os.path.exists(st.session_state['file_path']):
        with h5py.File(st.session_state['file_path'], 'r') as f:
            if 'mtx' not in f:
                st.error("Nenhum dataset 'mtx' foi encontrado neste arquivo. Verifique se é uma matriz BGS válida.")
            else:
                # Carregar e formatar eixos
                distances = np.array(f['distances']) if 'distances' in f else np.arange(f['mtx'].shape[1])
                
                # Suporta shape (1, 8500, 512) -> pega a fatia do tempo 0
                mtx_data = np.array(f['mtx'][0]) if len(f['mtx'].shape) == 3 else np.array(f['mtx'])
                
                # Calcular o eixo de frequência a partir dos metadados globais FEBUS
                freq_step = float(f.attrs.get('freq_step', [-1.0])[0]) if 'freq_step' in f.attrs else -1.0
                freq_offset = float(f.attrs.get('freq_offset', [0.0])[0]) if 'freq_offset' in f.attrs else 0.0
                
                num_freqs = mtx_data.shape[1]
                frequencies = np.arange(num_freqs) * freq_step + freq_offset
                
                st.success(f"Matriz carregada com sucesso! Shape interno: {mtx_data.shape[0]} instâncias x {mtx_data.shape[1]} varreduras de frequência.")
                
                # --- MAPA DE CALOR 2D ---
                st.header("1. Mapa de Calor Global (Heatmap)")
                st.markdown("Visão planificada em 2D de toda a fibra. (Downsampled para garantir rápida renderização em seu navegador).")
                
                step_d = max(1, len(distances) // 1000)
                dec_dist = distances[::step_d]
                dec_freq = frequencies
                dec_mtx = mtx_data[::step_d, :]
                
                fig_heat = go.Figure(data=go.Heatmap(
                    z=dec_mtx.T,
                    x=dec_dist,
                    y=dec_freq,
                    colorscale='Jet'
                ))
                fig_heat.update_layout(xaxis_title='Distância (m)', yaxis_title='Frequência (MHz)', height=500)
                st.plotly_chart(fig_heat, use_container_width=True)
                
                st.divider()
                
                # --- GRÁFICO 3D ---
                st.header("2. Gráfico 3D Interativo (Superfície)")
                st.markdown("Selecione um corte de alguns índices para rotacionar uma parcela realística em 3D, avaliando o perfil de montanha do espectro.")
                
                c1, c2 = st.columns(2)
                with c1:
                    start_idx = st.number_input("Índice de Início", min_value=0, max_value=len(distances)-2, value=min(400, len(distances)//2))
                with c2:
                    end_idx = st.number_input("Índice de Término", min_value=start_idx+1, max_value=len(distances), value=min(start_idx+100, len(distances)))
                    
                st.info(f"O trecho 3D cobrirá as distâncias entre {distances[start_idx]:.2f}m e {distances[end_idx-1]:.2f}m.")
                    
                if st.button("Gerar Superfície 3D", type="primary"):
                    with st.spinner("Construindo geometria 3D..."):
                        slice_mtx = mtx_data[start_idx:end_idx, :]
                        slice_dist = distances[start_idx:end_idx]
                        
                        fig_3d = go.Figure(data=[go.Surface(z=slice_mtx.T, x=slice_dist, y=frequencies, colorscale='Jet')])
                        fig_3d.update_layout(
                            title=f'Superfície 3D da Matriz de Ganho',
                            scene=dict(
                                xaxis_title='Distância (m)',
                                yaxis_title='Frequência (MHz)',
                                zaxis_title='Amplitude BGS'
                            ),
                            autosize=False,
                            width=1000, 
                            height=800,
                            margin=dict(l=65, r=50, b=65, t=90)
                        )
                        st.plotly_chart(fig_3d, use_container_width=True)
                    
                st.divider()
                
                # --- CORTE TRANSVERSAL ---
                st.header("3. Perfil de Frequência Isolado (Corte Transversal)")
                st.markdown("Avalie matematicamente a curva exata do BGS sobre um ponto específico.")
                
                target_idx = st.slider("Selecione o Índice de Distância Exato:", 0, len(distances)-1, value=start_idx)
                target_dist = distances[target_idx]
                spectrum = mtx_data[target_idx, :]
                
                fig_line = go.Figure(data=go.Scatter(x=frequencies, y=spectrum, mode='lines', line=dict(color='orange', width=2)))
                fig_line.update_layout(
                    title=f'Curva Espectral na Distância = {target_dist:.2f} m', 
                    xaxis_title='Frequência (MHz)', 
                    yaxis_title='Amplitude',
                    height=500
                )
                st.plotly_chart(fig_line, use_container_width=True)
                
    else:
         st.warning("Insira no painel à esquerda um caminho de arquivo existente.")
except Exception as e:
    import traceback
    st.error(f"Erro ao processar o arquivo: {e}")
    st.code(traceback.format_exc())
