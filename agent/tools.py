"""Tools used by the Weekend Buddy planner."""
def filter_activities(activities, budget, available_minutes, category="either", energy="any", company="any", excluded_ids=()):
    excluded = set(excluded_ids)
    result = []
    for a in activities:
        if a["id"] in excluded or a["estimated_cost"] > budget or a["duration_minutes"] > available_minutes:
            continue
        if category != "either" and a["category"] != category:
            continue
        if energy != "any" and a["energy"] != energy:
            continue
        if company == "solo" and a["social"] == "group":
            continue
        if company == "group" and a["social"] == "solo":
            continue
        result.append(a)
    return result

def build_itinerary(activities, budget, available_minutes, max_items=4):
    remaining = sorted(activities, key=lambda a: (a["estimated_cost"], a["duration_minutes"]))
    selected, cost, minutes, categories = [], 0, 0, set()
    while remaining and len(selected) < max_items:
        fitting = [a for a in remaining if cost + a["estimated_cost"] <= budget and minutes + a["duration_minutes"] <= available_minutes]
        if not fitting:
            break
        fitting.sort(key=lambda a: (0 if a["category"] not in categories else 1, a["estimated_cost"], a["duration_minutes"]))
        choice = fitting[0]
        selected.append(choice)
        cost += choice["estimated_cost"]
        minutes += choice["duration_minutes"]
        categories.add(choice["category"])
        remaining = [a for a in remaining if a["id"] != choice["id"]]
    return selected
