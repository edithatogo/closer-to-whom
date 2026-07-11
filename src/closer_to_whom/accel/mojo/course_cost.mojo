# Experimental Mojo accelerator. Promotion requires differential and benchmark gates.

fn course_distance(one_way_km: Float64, visits: Float64) -> Float64:
    return 2.0 * one_way_km * visits

fn course_minutes(one_way_minutes: Float64, visits: Float64) -> Float64:
    return 2.0 * one_way_minutes * visits

fn course_direct_cost(
    one_way_km: Float64,
    visits: Float64,
    cost_per_km: Float64,
    fixed_cost_per_visit: Float64,
) -> Float64:
    return course_distance(one_way_km, visits) * cost_per_km + visits * fixed_cost_per_visit

fn main():
    # Deterministic canary output consumed by scripts/mojo_canary.py.
    print(course_direct_cost(60.0, 18.0, 0.37, 12.0))
