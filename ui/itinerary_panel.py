"""Renders the live itinerary canvas (right pane) from the Itinerary model."""
import streamlit as st

from models.trip import Itinerary, TripInfo


def render_itinerary(trip_info: TripInfo, itinerary: Itinerary) -> None:
    st.subheader("🧭 Live Itinerary")

    if not trip_info.destination and itinerary.is_empty():
        st.info("Your itinerary will appear here as we chat.")
        return

    if itinerary.trip_summary or trip_info.destination:
        st.markdown("**Trip Summary**")
        st.write(itinerary.trip_summary or f"Trip to {trip_info.destination}")

    with st.expander("Transportation", expanded=bool(itinerary.transportation)):
        if itinerary.transportation:
            for leg in itinerary.transportation:
                st.markdown(f"- **{leg['mode'].replace('_', ' ').title()}** ({leg.get('distance_km', '?')} km) — {leg['rationale']}")
        else:
            st.caption("Not yet planned.")

    with st.expander("Hotels", expanded=bool(itinerary.hotels)):
        if itinerary.hotels:
            for hotel in itinerary.hotels:
                st.markdown(f"- {hotel}")
        else:
            st.caption("Not yet selected.")

    with st.expander("Daily Plans", expanded=bool(itinerary.daily_plans)):
        if itinerary.daily_plans:
            for day in itinerary.daily_plans:
                st.markdown(f"- {day}")
        else:
            st.caption("Not yet built.")

    with st.expander("Estimated Budget", expanded=bool(itinerary.estimated_budget)):
        budget = itinerary.estimated_budget
        if budget:
            currency = budget["currency"]
            if trip_info.budget:
                st.caption(f"Traveler-stated budget: {trip_info.budget}")
            st.metric(f"Estimated Total ({budget['nights']} nights, {budget['travelers']} traveler(s))", f"{currency} {budget['total']:,}")
            st.markdown(
                f"- Accommodation: {currency} {budget['accommodation']:,} — {budget['notes']['accommodation']}\n"
                f"- Transportation: {currency} {budget['transportation']:,} — {budget['notes']['transportation']}\n"
                f"- Food: {currency} {budget['food']:,} — {budget['notes']['food']}\n"
                f"- Activities: {currency} {budget['activities']:,} — {budget['notes']['activities']}"
            )
        elif trip_info.budget:
            st.write(trip_info.budget)
        else:
            st.caption("Not yet estimated.")

    with st.expander("Travel Checklist & Packing"):
        if itinerary.checklist:
            for item in itinerary.checklist:
                st.checkbox(item, key=f"chk_{item}")
        if itinerary.packing_suggestions:
            st.markdown("**Packing suggestions**")
            for item in itinerary.packing_suggestions:
                st.markdown(f"- {item}")
        if not itinerary.checklist and not itinerary.packing_suggestions:
            st.caption("Not yet generated.")

    with st.expander("Trip Details Collected So Far"):
        st.json(
            {
                "destination": trip_info.destination,
                "departure_city": trip_info.departure_city,
                "dates": f"{trip_info.start_date or '?'} - {trip_info.end_date or '?'}",
                "budget": trip_info.budget,
                "travelers": trip_info.travelers_count,
                "purpose": trip_info.purpose,
                "interests": trip_info.interests,
                "travel_style": trip_info.travel_style,
            }
        )
