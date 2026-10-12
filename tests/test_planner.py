from agent.tools import filter_activities, build_itinerary
from agent.planner import apply_preference_text, create_plan

SAMPLE = [
 {"id":"walk","name":"Walk","category":"outdoor","duration_minutes":30,"estimated_cost":0,"energy":"moderate","social":"either","description":"","icon":"🌿"},
 {"id":"read","name":"Read","category":"indoor","duration_minutes":20,"estimated_cost":0,"energy":"relaxing","social":"solo","description":"","icon":"📚"},
 {"id":"event","name":"Event","category":"outdoor","duration_minutes":90,"estimated_cost":500,"energy":"active","social":"group","description":"","icon":"🎟️"}
]
def test_budget_and_time_filters():
    result = filter_activities(SAMPLE, 0, 40)
    assert {a["id"] for a in result} == {"walk","read"}
def test_itinerary_constraints():
    result = build_itinerary(SAMPLE, 0, 35)
    assert sum(a["estimated_cost"] for a in result) <= 0
    assert sum(a["duration_minutes"] for a in result) <= 35
def test_text_adjustment():
    p = apply_preference_text({"budget":500,"available_minutes":240,"category":"either","energy":"any"}, "cheaper and indoors")
    assert p["budget"] == 0 and p["category"] == "indoor"
def test_plan_summary():
    p = create_plan({"budget":100,"available_minutes":60,"category":"either","energy":"any","company":"any","max_items":3}, SAMPLE)
    assert p["total_cost"] <= 100 and p["total_minutes"] <= 60
