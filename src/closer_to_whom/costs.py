"""Travel, time, reimbursement, and provider cost estimation."""

from __future__ import annotations

from dataclasses import dataclass

from closer_to_whom.models import CostRates


@dataclass(frozen=True, slots=True)
class CourseBurden:
    """Course-level travel and cost outcomes under one assignment."""

    course_travel_km: float
    course_travel_minutes: float
    course_on_site_minutes: float
    patient_direct_cost_nzd: float
    patient_whanau_cost_nzd: float
    payer_cost_nzd: float
    provider_cost_nzd: float
    societal_cost_nzd: float

    def __post_init__(self) -> None:
        values = (
            self.course_travel_km,
            self.course_travel_minutes,
            self.course_on_site_minutes,
            self.patient_direct_cost_nzd,
            self.patient_whanau_cost_nzd,
            self.payer_cost_nzd,
            self.provider_cost_nzd,
            self.societal_cost_nzd,
        )
        if any(value < -1e-9 for value in values):
            raise ValueError("Burden outputs must be non-negative")


def calculate_course_burden(
    *,
    one_way_km: float,
    one_way_minutes: float,
    visits: float,
    course_on_site_minutes: float,
    rates: CostRates,
    public_transport_share: float = 0.0,
    nta_eligible_share: float = 0.0,
    home_provider_round_trip_km: float = 0.0,
    home_provider_minutes: float = 0.0,
) -> CourseBurden:
    """Estimate transparent course-level costs from explicit components."""
    values = (
        one_way_km,
        one_way_minutes,
        visits,
        course_on_site_minutes,
        public_transport_share,
        nta_eligible_share,
        home_provider_round_trip_km,
        home_provider_minutes,
    )
    if any(value < 0 for value in values):
        raise ValueError("Distance, time, visits, and shares cannot be negative")
    if public_transport_share > 1 or nta_eligible_share > 1:
        raise ValueError("Shares must be between zero and one")

    round_trip_km = one_way_km * 2.0
    round_trip_minutes = one_way_minutes * 2.0
    course_travel_km = round_trip_km * visits
    course_travel_minutes = round_trip_minutes * visits

    private_share = 1.0 - public_transport_share
    vehicle_running = course_travel_km * rates.vehicle_running_cost_per_km * private_share
    public_fares = visits * rates.public_transport_fare_per_round_trip * public_transport_share
    parking = visits * rates.parking_cost_per_visit * private_share
    patient_direct = vehicle_running + public_fares + parking

    reimbursement = course_travel_km * rates.nta_reimbursement_per_km * nta_eligible_share
    payer_cost = reimbursement

    patient_hours = (course_travel_minutes + course_on_site_minutes) / 60.0
    companion_hours = patient_hours * rates.companion_probability
    patient_time = patient_hours * rates.patient_time_value_per_hour
    companion_time = companion_hours * rates.companion_time_value_per_hour
    patient_whanau = max(0.0, patient_direct - reimbursement) + patient_time + companion_time

    provider_travel_cost = home_provider_round_trip_km * rates.provider_vehicle_cost_per_km
    provider_time_cost = home_provider_minutes / 60.0 * rates.provider_time_value_per_hour
    provider_cost = provider_travel_cost + provider_time_cost

    # Reimbursement is a transfer and is excluded from societal resource cost.
    societal = patient_direct + patient_time + companion_time + provider_cost
    return CourseBurden(
        course_travel_km=course_travel_km,
        course_travel_minutes=course_travel_minutes,
        course_on_site_minutes=course_on_site_minutes,
        patient_direct_cost_nzd=patient_direct,
        patient_whanau_cost_nzd=patient_whanau,
        payer_cost_nzd=payer_cost,
        provider_cost_nzd=provider_cost,
        societal_cost_nzd=societal,
    )
