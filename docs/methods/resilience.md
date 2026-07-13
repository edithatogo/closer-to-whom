# Resilience and outage sensitivity

The resilience slice evaluates declared facility-outage sets against the
aggregate assignment cube. It reports expected courses assigned to facilities
in the outage set, the remainder of the assignment cube, and the affected
share for each scenario and pathway.

The remainder is **retained assignment**, not successfully rerouted demand.
The implementation deliberately sets `rerouting_modelled` and
`observed_capacity_claim` to `false`: the public service census is not yet
frozen, and the repository has no evidence of spare or substitute capacity.
Synthetic fixtures are suitable for testing invariants only and cannot support
operational or clinical conclusions.
