data = {} #this holds all the data from STELUM, PULSE, and .eig files during the session
#this is actually necessary as a dcc.Store only has only ~10MB of data if storage_type == "session"
#which is clearly cooked for .eig files...
graph_options = {}
line_options = {}

#['mass', 'lq_envl', 'lq_core', 'core_he', 'core_o', 'core_z', 'pf_envl', 'delta_core', 'lq_diff', 'diff_h', 'pf_diff', 'lq_flash', 'flash_c', 'pf_flash', 'conv_alpha', 'opc_metal', 'use_filters', 'lmin', 'lmax', 'period_scan', 'pmin', 'pmax', 'dp', 'frequency_scan', 'fmin', 'fmax', 'nf', 'nelems', 'compute_nad', 'mode_output', 'ad_filter', 'ad_highres']
## THIS IS ALL POSSIBLE KEYS
kept_columns = ["mass","lq_envl","lq_core","core_he","pf_envl","delta_core","lq_diff","diff_h","pf_diff","lq_flash","flash_c","pf_flash","lmin","lmax"]