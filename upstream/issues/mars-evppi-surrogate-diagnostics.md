# feat: surrogate diagnostics for EVPPI, PSA, and optimisation emulators

Add deterministic train/test splits, monotonicity options, calibration and residual diagnostics, extrapolation flags, Arrow serialisation, and error propagation into EVPPI or optimisation decisions. A surrogate must not be promoted without comparing decision loss against the exact model.

Project oracle: transparent quantile-bin EVPPI in `src/closer_to_whom/voi.py`; MARS is an optional higher-performance backend.
