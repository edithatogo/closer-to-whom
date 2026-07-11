# Mojo accelerator track

This kernel is experimental and non-release-critical. It may be promoted only when:

1. a pinned Mojo toolchain is available in CI;
2. scalar, vector, boundary, property, and fuzz differential tests match the NumPy oracle;
3. outputs are reproducible across two clean builds;
4. benchmark speed-up exceeds the threshold in `assumptions/performance-budgets.yaml`;
5. wheel, Docker, and Hugging Face deployment paths remain functional without Mojo;
6. an ADR records the portability and maintenance trade-off.

Until those gates pass, Python/Polars/Arrow remain canonical and JAX is the supported optional accelerator.
