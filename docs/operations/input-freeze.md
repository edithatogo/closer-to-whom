# Public input freeze

`data/public/input-freeze.yaml` is the machine-readable gate for the public aggregate demand and
geography inputs. It records the source IDs, dataset versions, licence state, evidence grade, and
retrieval receipt needed before an input can become frozen.

The committed manifest is `frozen` for authorised local use. Every included row provides a dated
version, factual licence state, retrieval receipt, evidence grade, and explicit redistribution
policy. This authorisation does not turn restricted source payloads into redistributable data or
convert missing values into zero. `make contracts` validates the freeze without downloading data.
