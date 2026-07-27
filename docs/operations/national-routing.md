# National road-routing runbook

The release road matrix uses only the dated network and engine identities in
`data/public/routing-network-freeze.yaml`. The public OSRM demonstration server is never an input.

1. Download `new-zealand-260723.osm.pbf` into `data/raw/osrm/`.
2. Confirm its size and published MD5, then calculate and record its SHA-256 in the freeze file.
3. Pull `ghcr.io/project-osrm/osrm-backend@sha256:a7091038e39a73659767f34ef2d389909b42ea80b09bd2bdca482dce2991cbad` and record the resolved image digest.
4. Build the MLD graph:

   ```text
   docker compose -f compose.osrm.yaml run --rm osrm-extract
   docker compose -f compose.osrm.yaml run --rm osrm-partition
   docker compose -f compose.osrm.yaml run --rm osrm-customize
   ```

5. Start the loopback-only service:

   ```text
   docker compose -f compose.osrm.yaml up osrm-routed
   ```

6. Materialize the matrix only after the aggregate demand and facility registries are complete:

   ```text
   uv run python scripts/materialize_route_costs.py --osrm-base-url http://127.0.0.1:5000 --osrm-version 26.7.3
   ```

The raw PBF, generated graph, and derived matrix remain ignored. Release evidence must record the
PBF SHA-256, container digest, graph command, route cache fingerprint, input fingerprints, row
counts, retrieval time, and the non-approximation state.
