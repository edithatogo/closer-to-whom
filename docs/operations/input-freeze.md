# Public input freeze

`data/public/input-freeze.yaml` is the machine-readable gate for the public aggregate demand and
geography inputs. It records the source IDs, dataset versions, licence state, evidence grade, and
retrieval receipt needed before an input can become frozen.

The committed manifest is intentionally `pending`. That is an explicit evidence boundary, not a
claim that the input is absent or that demand is zero. A frozen manifest must provide a dated
version, licence state, retrieval receipt, and evidence grade for every input, with no pending rows.
`make contracts` validates this state without downloading network data.
