import streamlit as st
import h5py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="HDF5 Data Viewer", layout="wide")

st.title("HDF5 Data Viewer 📊")
st.markdown("Explore, slice, plot, and export HDF5 data directly from your browser.")

# ---------------------------------------------------------
# Sidebar: File Loading
# ---------------------------------------------------------
st.sidebar.header("1. Load File")
file_path = st.sidebar.text_input("Path to .h5 File:", value="mock_febus_data_10k.h5")

def get_h5_structure(filepath):
    """Lê a estrutura do arquivo H5 e retorna grupos, datasets e atributos."""
    from typing import Any
    structure: dict[str, Any] = {"datasets": {}, "groups": [], "attributes": {}}
    
    if not os.path.exists(filepath):
        return None, f"File not found: {filepath}"
        
    try:
        def visitor(name, node):
            if isinstance(node, h5py.Dataset):
                structure["datasets"][name] = {
                    "shape": node.shape,
                    "dtype": str(node.dtype),
                    "attrs": dict(node.attrs)
                }
            elif isinstance(node, h5py.Group):
                structure["groups"].append(name)
                
        with h5py.File(filepath, 'r') as f:
            structure["attributes"] = dict(f.attrs)
            f.visititems(visitor)
            
        return structure, "Success"
    except Exception as e:
        return None, str(e)

def parse_slice_string(slice_str):
    """Converte uma string como '0, 450:550' em um objeto slice do Python."""
    if not slice_str or slice_str.strip() == ":":
        return slice(None)
        
    parts = slice_str.split(',')
    slices = []
    
    for p in parts:
        p = p.strip()
        if p == ':':
            slices.append(slice(None))
        elif ':' in p:
            start, stop = p.split(':')
            start = int(start) if start else None
            stop = int(stop) if stop else None
            slices.append(slice(start, stop))
        else:
            slices.append(int(p))
            
    return tuple(slices) if len(slices) > 1 else slices[0]

# ---------------------------------------------------------
# Main App
# ---------------------------------------------------------

if st.sidebar.button("Load / Refresh"):
    if file_path:
        st.session_state['file_path'] = file_path

if 'file_path' in st.session_state:
    struct, msg = get_h5_structure(st.session_state['file_path'])
    
    if struct is None:
        st.error(f"Error reading file: {msg}")
    else:
        st.success(f"File loaded successfully! ({st.session_state['file_path']})")
        
        # --- Section 1: Metadata and Structure ---
        with st.expander("View File Structure & Metadata", expanded=False):
            st.subheader("Global Attributes (Root)")
            if struct["attributes"]:
                st.json(struct["attributes"])
            else:
                st.write("No global attributes found.")
                
            st.subheader("Available Datasets")
            for ds_name, info in struct["datasets"].items():
                st.markdown(f"**`{ds_name}`** | Shape: `{info['shape']}` | Type: `{info['dtype']}`")
                if info['attrs']:
                    st.json(info['attrs'])
        
        st.divider()
        
        # --- Section 2: Plotting and Slicing ---
        st.header("2. Data Selection & Slicing")
        st.markdown("Choose the Datasets for X and Y.")
        
        col1, col2 = st.columns(2)
        
        dataset_names = list(struct["datasets"].keys())
        
        with col1:
            st.subheader("X Axis")
            x_dataset = st.selectbox("Dataset for X (Base):", dataset_names, index=0 if len(dataset_names) > 0 else 0)
            x_shape = struct["datasets"][x_dataset]["shape"] if x_dataset else "N/A"
            st.caption(f"Shape: {x_shape}")
            
            x_dim_size = x_shape[0] if x_shape != "N/A" and len(x_shape) > 0 else 1
            
            # --- Initialize Session State for synchronized widgets ---
            if "x_slider" not in st.session_state:
                st.session_state["x_slider"] = (0, x_dim_size)
            if "x_start_input" not in st.session_state:
                st.session_state["x_start_input"] = 0
            if "x_end_input" not in st.session_state:
                st.session_state["x_end_input"] = x_dim_size

            # Callbacks for Two-Way Binding
            def update_from_slider():
                st.session_state["x_start_input"] = st.session_state["x_slider"][0]
                st.session_state["x_end_input"] = st.session_state["x_slider"][1]
                
            def update_from_inputs():
                start = st.session_state["x_start_input"]
                end = st.session_state["x_end_input"]
                # Ensure values are within bounds
                start = max(0, min(start, x_dim_size - 1))
                end = max(start + 1, min(end, x_dim_size))
                st.session_state["x_slider"] = (start, end)
            
            with st.expander("Define Interval (Base Slicing X)", expanded=True):
                st.markdown(f"**Max Size:** {x_dim_size}")
                
                # Manual start/end inputs in columns
                c1, c2 = st.columns(2)
                with c1:
                     st.number_input("Start", min_value=0, max_value=x_dim_size-1, key="x_start_input", on_change=update_from_inputs)
                with c2:
                     st.number_input("End", min_value=1, max_value=x_dim_size, key="x_end_input", on_change=update_from_inputs)
                
                # Sincronizado Slider
                slice_range = st.slider("Or adjust visually:", 0, x_dim_size, key="x_slider", on_change=update_from_slider)
                
                x_slice = slice(slice_range[0], slice_range[1])
                st.info(f"The plot will have {slice_range[1] - slice_range[0]} points on the X Axis.")
                
        with col2:
            st.subheader("Y Axis")
            y_index = 1 if len(dataset_names) > 1 else 0
            y_dataset = st.selectbox("Dataset for Y:", dataset_names, index=y_index)
            y_shape = struct["datasets"][y_dataset]["shape"] if y_dataset else "N/A"
            st.caption(f"Shape: {y_shape}")
            
            y_slice_list = []
            
            with st.expander("Y Axis Synchronization", expanded=True):
                 if y_shape != "N/A":
                     if len(y_shape) <= 1:
                         st.write("1D Dataset. Interval automatically synchronized with X Axis.")
                         y_slice_list = [x_slice]
                     else:
                         st.write("Multi-dimensional Dataset detected!")
                         axis_dim = st.radio(
                             "Which dimension corresponds to the X Axis (Interval)?", 
                             options=range(len(y_shape)), 
                             format_func=lambda x: f"Dim {x} (Size: {y_shape[x]})",
                             horizontal=True
                         )
                         
                         for dim_idx, dim_size in enumerate(y_shape):
                             if dim_idx == axis_dim:
                                 st.success(f"Dimension {dim_idx} will follow the X Axis slice.")
                                 y_slice_list.append(x_slice)
                             else:
                                 st.warning(f"Dimension {dim_idx} represents the traces/time. Select a range to average:")
                                 c_interval = st.slider(f"Range for Dim {dim_idx}", 0, dim_size-1, (0, min(10, dim_size-1)))
                                 y_slice_list.append(slice(c_interval[0], c_interval[1] + 1))
                                 st.session_state['y_trace_axis'] = dim_idx
                 y_slice = tuple(y_slice_list) if len(y_slice_list) > 1 else y_slice_list[0] if y_slice_list else slice(None)
                
        from scipy.signal import butter, filtfilt, savgol_filter, medfilt
        from scipy.fft import fft, fftfreq
        
        st.divider()
        st.header("3. Advanced Digital Filters (DSP) 〰️")
        
        # UI configuration for filters using Tabs
        tab_smooth, tab_freq, tab_spike, tab_cascade, tab_fft, tab_quant = st.tabs(["Smoothing", "Frequency Cutoff", "Spikes", "Cascading", "Spectral Analysis", "Quantitative"])
        
        with tab_smooth:
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("### Moving Average")
                use_moving_avg = st.checkbox("Enable Moving Average", value=False)
                if use_moving_avg:
                    ma_window = st.number_input("Window Size (points)", min_value=2, max_value=max(2, x_dim_size//2), value=min(10, max(2, x_dim_size//10)), step=1)
            with col_s2:
                st.markdown("### Savitzky-Golay")
                use_savgol = st.checkbox("Enable Savitzky-Golay", value=False, help="Preserves real peak heights while removing noise.")
                if use_savgol:
                    sg_window = st.number_input("Window Size (Odd)", min_value=3, max_value=max(3, x_dim_size//2), value=min(11, max(3, x_dim_size//10)|1), step=2)
                    # Enforce odd window logic indirectly since step=2 might jump from an even if manually typed
                    if sg_window % 2 == 0:
                        sg_window += 1
                        st.warning("The Savitzky-Golay window size must be odd. Automatically adjusted by +1.")
                    sg_order = st.number_input("Polynomial Order", min_value=1, max_value=min(5, sg_window-1), value=2)

        with tab_freq:
            st.markdown("### Butterworth")
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                use_bw_low = st.checkbox("Low-Pass (Remove Fast Noise)", value=False)
                if use_bw_low:
                    bw_low_order = st.number_input("Order (Low)", min_value=1, max_value=10, value=3, key="bwl_ord")
                    bw_low_cutoff = st.slider("Normalized Cutoff (Low)", 0.01, 0.99, 0.1, 0.01, key="bwl_cut")
            with c_f2:
                use_bw_high = st.checkbox("High-Pass (Remove Slow Drifts)", value=False)
                if use_bw_high:
                    bw_high_order = st.number_input("Order (High)", min_value=1, max_value=10, value=3, key="bwh_ord")
                    bw_high_cutoff = st.slider("Normalized Cutoff (High)", 0.01, 0.99, 0.02, 0.01, key="bwh_cut")

        with tab_spike:
            st.markdown("### Median Filter")
            use_median = st.checkbox("Enable Median Filter", value=False, help="Excellent for removing isolated absurd 'spikes' (e.g., dirty reflections).")
            if use_median:
                med_kernel = st.number_input("Kernel Size (Odd)", min_value=3, max_value=99, value=3, step=2)
                if med_kernel % 2 == 0:
                    med_kernel += 1
                    st.warning("The kernel size must be odd.")

        with tab_cascade:
            st.markdown("### Cascading Filters")
            use_cascade = st.checkbox("Enable Cascaded Filters", value=False, help="Apply multiple filters sequentially to the same dataset.")
            
            cascade_configs = []
            if use_cascade:
                num_stages = st.number_input("Number of Stages", min_value=2, max_value=4, value=2, step=1)
                
                cols = st.columns(num_stages)
                for i in range(num_stages):
                    with cols[i]:
                        st.markdown(f"**Stage {i+1}**")
                        filter_type = st.selectbox(
                            "Filter Type", 
                            ["None", "Moving Average", "Savitzky-Golay", "Median", "Low-Pass", "High-Pass"], 
                            key=f"casc_type_{i}"
                        )
                        
                        config = {"type": filter_type}
                        if filter_type == "Moving Average":
                            config["window"] = st.number_input("Window", min_value=2, value=10, key=f"casc_ma_w_{i}")
                        elif filter_type == "Savitzky-Golay":
                            w = st.number_input("Window (Odd)", min_value=3, value=11, key=f"casc_sg_w_{i}", step=2)
                            if w % 2 == 0: w += 1
                            config["window"] = w
                            config["order"] = st.number_input("Order", min_value=1, value=2, key=f"casc_sg_o_{i}")
                        elif filter_type == "Median":
                            k = st.number_input("Kernel (Odd)", min_value=3, value=3, key=f"casc_med_k_{i}", step=2)
                            if k % 2 == 0: k += 1
                            config["kernel"] = k
                        elif filter_type in ["Low-Pass", "High-Pass"]:
                            config["order"] = st.number_input("Order", min_value=1, value=3, key=f"casc_bw_o_{i}")
                            config["cutoff"] = st.slider("Cutoff", 0.01, 0.99, 0.1, 0.01, key=f"casc_bw_c_{i}")
                            
                        cascade_configs.append(config)

        with tab_fft:
            st.markdown("### Fast Fourier Transform (FFT)")
            use_fft = st.checkbox("Generate Spectrum Plot (FFT)", value=False, help="Generates a second chart showing the spatial frequencies contained in the data.")

        with tab_quant:
            st.markdown("### Quantitative Thresholds")
            use_quant = st.checkbox("Enable Quantitative Analysis", value=False, help="Find specific spatial intervals where the signal violates defined thresholds.")
            if use_quant:
                c_q1, c_q2 = st.columns(2)
                with c_q1:
                    quant_pos_thresh = st.number_input("Positive Threshold (+)", value=31.0, step=1.0)
                with c_q2:
                    quant_neg_thresh = st.number_input("Negative Threshold (-)", value=20.0, step=1.0)

        if st.button("Load Data for Plotting", type="primary"):
            try:
                with h5py.File(st.session_state['file_path'], 'r') as f:
                    data_x = f[x_dataset][x_slice]
                    data_y = f[y_dataset][y_slice]
                    
                data_x = np.array(data_x).flatten()
                data_y = np.array(data_y)
                
                # If Y data was multidimensional and an interval was selected, average the traces
                if len(data_y.shape) > 1 and 'y_trace_axis' in st.session_state:
                     # e.g., Shape (10, 1000). If Dim 0 is the trace axis, we average across axis 0.
                     # However, since we already sliced y_slice exactly to shape [Traces, Spatials],
                     # we need to accurately collapse the dimension that is NOT following X.
                     # It's always Axis 0 if y_trace_axis was 0 initially, assuming typical HDF5 reading logic.
                     axis_to_average = 0 if st.session_state['y_trace_axis'] == 0 else 1
                     data_y = np.mean(data_y, axis=axis_to_average)
                     
                data_y = data_y.flatten()
                
                if len(data_x) != len(data_y):
                    st.error(f"Dimension Error: X has {len(data_x)} and Y has {len(data_y)}.")
                else:
                    st.session_state['raw_data_x'] = data_x
                    st.session_state['raw_data_y'] = data_y
                    st.session_state['plot_x_name'] = x_dataset
                    st.session_state['plot_y_name'] = y_dataset
                    st.success(f"Data Loaded! The filters will apply instantly from now on.")
            except Exception as e:
                import traceback
                st.error(f"Error during slicing: {e}")
                st.code(traceback.format_exc())
                
        if 'raw_data_x' in st.session_state and 'raw_data_y' in st.session_state:
            data_x = st.session_state['raw_data_x']
            data_y = st.session_state['raw_data_y']
            px_name = st.session_state['plot_x_name']
            py_name = st.session_state['plot_y_name']
            
            df_export = pd.DataFrame({
                px_name: data_x,
                py_name: data_y
            })
            
            # Apply Filters Dynamics
            plots_to_make = []
            
            try:
                if use_moving_avg:
                    ma = np.convolve(data_y, np.ones(ma_window)/ma_window, mode='same')
                    df_export[f'MovingAverage_w{ma_window}'] = ma
                    plots_to_make.append((ma, f'Moving Average (w={ma_window})', 'tab:orange'))
                    
                if use_savgol:
                    sg = savgol_filter(data_y, window_length=sg_window, polyorder=sg_order)
                    df_export[f'SavitzkyGolay_w{sg_window}_o{sg_order}'] = sg
                    plots_to_make.append((sg, f'Savitzky-Golay (w={sg_window}, o={sg_order})', 'tab:green'))
                    
                if use_median:
                    med = medfilt(data_y, kernel_size=med_kernel)
                    df_export[f'Median_k{med_kernel}'] = med
                    plots_to_make.append((med, f'Median Filter (k={med_kernel})', 'tab:purple'))
                    
                if use_bw_low:
                    b, a = butter(bw_low_order, bw_low_cutoff, btype='low', analog=False)
                    bwl = filtfilt(b, a, data_y)
                    df_export[f'LowPass_o{bw_low_order}_c{bw_low_cutoff}'] = bwl
                    plots_to_make.append((bwl, f'Low-Pass (o={bw_low_order}, c={bw_low_cutoff})', 'tab:red'))
                    
                if use_bw_high:
                    b, a = butter(bw_high_order, bw_high_cutoff, btype='high', analog=False)
                    bwh = filtfilt(b, a, data_y)
                    df_export[f'HighPass_o{bw_high_order}_c{bw_high_cutoff}'] = bwh
                    plots_to_make.append((bwh, f'High-Pass (o={bw_high_order}, c={bw_high_cutoff})', 'tab:cyan'))
                    
                if use_cascade:
                    current_data = data_y.copy()
                    cascade_name_parts = []
                    
                    for conf in cascade_configs:
                        ftype = conf["type"]
                        if ftype == "None":
                            continue
                        elif ftype == "Moving Average":
                            w = conf["window"]
                            current_data = np.convolve(current_data, np.ones(w)/w, mode='same')
                            cascade_name_parts.append(f"MA({w})")
                        elif ftype == "Savitzky-Golay":
                            current_data = savgol_filter(current_data, window_length=conf["window"], polyorder=conf["order"])
                            cascade_name_parts.append(f"SG({conf['window']},{conf['order']})")
                        elif ftype == "Median":
                            current_data = medfilt(current_data, kernel_size=conf["kernel"])
                            cascade_name_parts.append(f"Med({conf['kernel']})")
                        elif ftype == "Low-Pass":
                            b, a = butter(conf["order"], conf["cutoff"], btype='low', analog=False)
                            current_data = filtfilt(b, a, current_data)
                            cascade_name_parts.append(f"LP({conf['cutoff']})")
                        elif ftype == "High-Pass":
                            b, a = butter(conf["order"], conf["cutoff"], btype='high', analog=False)
                            current_data = filtfilt(b, a, current_data)
                            cascade_name_parts.append(f"HP({conf['cutoff']})")
                            
                    if cascade_name_parts:
                        cascade_full_name = " + ".join(cascade_name_parts)
                        # Remove problematic chars for CSV column name
                        col_name = f"Cascade_{'_'.join(cascade_name_parts)}".replace('(', '').replace(')', '').replace(',', '_')
                        df_export[col_name] = current_data
                        plots_to_make.append((current_data, f'Cascade: {cascade_full_name}', 'tab:brown'))
                    
                st.session_state['plot_data'] = df_export
                
                # --- Plot Principal ---
                fig, ax = plt.subplots(figsize=(10, 5))
                alpha_orig = 0.3 if len(plots_to_make) > 0 else 1.0
                ax.plot(data_x, data_y, label=f'Original ({py_name})', color='black', alpha=alpha_orig, linestyle='-' if alpha_orig == 1.0 else ':')
                
                for pt in plots_to_make:
                     ax.plot(data_x, pt[0], label=pt[1], color=pt[2], linewidth=1.5)
                
                if use_quant:
                    ax.axhline(quant_pos_thresh, color='red', linestyle='--', alpha=0.5, label=f'Threshold + ({quant_pos_thresh})')
                    ax.axhline(quant_neg_thresh, color='blue', linestyle='--', alpha=0.5, label=f'Threshold - ({quant_neg_thresh})')

                ax.set_xlabel(px_name)
                ax.set_ylabel(py_name)
                ax.set_title(f"Signal Visualization: {py_name} vs {px_name}")
                ax.grid(True, linestyle='--', alpha=0.7)
                ax.legend()
                
                st.pyplot(fig)
                
                # --- Plot FFT ---
                if use_fft:
                    st.subheader("Spectral Analysis (FFT)")
                    # Simple numerical difference for sampling rate approximation
                    if len(data_x) > 1:
                        dx = np.mean(np.diff(data_x))
                        if dx != 0:
                            n = len(data_y)
                            yf = fft(data_y)
                            xf = fftfreq(n, d=dx)[:n//2]
                            power = 2.0/n * np.abs(yf[0:n//2])
                            
                            fig_fft, ax_fft = plt.subplots(figsize=(10, 4))
                            ax_fft.plot(xf, power, color='indigo')
                            ax_fft.set_xlabel(f"Frequency Factor (1/{px_name})")
                            ax_fft.set_ylabel("Amplitude")
                            ax_fft.set_title("Frequency Spectrum of the Original Signal")
                            ax_fft.grid(True, alpha=0.3)
                            st.pyplot(fig_fft)
                        else:
                            st.warning("The X Axis does not have calculable spacing for FFT.")
                    else:
                        st.warning("Insufficient data for FFT.")
                
                # --- Quantitative Results ---
                if use_quant:
                    st.divider()
                    st.header("Quantitative Results (Threshold Analysis)")
                    
                    # Available traces
                    trace_names = [f"Original ({py_name})"] + [pt[1] for pt in plots_to_make]
                    target_trace = st.selectbox("Select trace to analyze for thresholds:", trace_names)
                    
                    if target_trace.startswith("Original"):
                        sig_data = data_y
                    else:
                        sig_data = next(pt[0] for pt in plots_to_make if pt[1] == target_trace)
                        
                    # Find exceedances
                    pos_mask = sig_data >= quant_pos_thresh
                    neg_mask = sig_data <= quant_neg_thresh
                    
                    def get_intervals(mask, x_arr, is_positive):
                        edges = np.diff(np.concatenate(([0], mask.view(np.int8), [0])))
                        starts = np.where(edges == 1)[0]
                        ends = np.where(edges == -1)[0] - 1
                        
                        results = []
                        for s, e in zip(starts, ends):
                            peak = float(np.max(sig_data[s:e+1])) if is_positive else float(np.min(sig_data[s:e+1]))
                            results.append((x_arr[s], x_arr[e], peak))
                        return results

                    pos_intervals = get_intervals(pos_mask, data_x, is_positive=True)
                    neg_intervals = get_intervals(neg_mask, data_x, is_positive=False)
                    
                    c_res1, c_res2 = st.columns(2)
                    with c_res1:
                        st.markdown(f"**Positive Exceedances (≥ {quant_pos_thresh})**")
                        if pos_intervals:
                            df_pos = pd.DataFrame(pos_intervals, columns=["Start (X)", "End (X)", "Peak Value"])
                            st.dataframe(df_pos, use_container_width=True)
                        else:
                            st.info("No positive threshold exceedances found.")
                            
                    with c_res2:
                        st.markdown(f"**Negative Exceedances (≤ {quant_neg_thresh})**")
                        if neg_intervals:
                            df_neg = pd.DataFrame(neg_intervals, columns=["Start (X)", "End (X)", "Trough Value"])
                            st.dataframe(df_neg, use_container_width=True)
                        else:
                            st.info("No negative threshold exceedances found.")
                
            except Exception as e:
                import traceback
                st.error(f"Error processing filters or generating plot: {e}")
                st.code(traceback.format_exc())
                
        # --- Seção 4: Exportação CSV ---
        if 'plot_data' in st.session_state:
            st.divider()
            st.header("4. Export Plot Data")
            
            df = st.session_state['plot_data']
            csv = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv,
                file_name=f"export_{x_dataset}_{y_dataset}.csv",
                mime="text/csv",
            )
else:
    st.info("Enter the file path in the sidebar and click 'Load'.")
