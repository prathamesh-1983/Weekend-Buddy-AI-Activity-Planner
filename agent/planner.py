"""Planning logic with optional Amazon Bedrock-generated explanation."""
import json, os
from pathlib import Path
from .tools import filter_activities, build_itinerary

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "activities.json"

def load_activities(path=DATA_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def apply_preference_text(preferences, request):
    p = preferences.copy()
    t = (request or "").lower()
    if any(w in t for w in ("indoors", "indoor", "inside", "at home")):
        p["category"] = "indoor"
    elif any(w in t for w in ("outdoors", "outdoor", "outside", "fresh air")):
        p["category"] = "outdoor"
    if any(w in t for w in ("cheaper", "less money", "low budget", "free only", "free activities")):
        p["budget"] = 0
    if any(w in t for w in ("shorter", "less time", "quick", "30 minutes", "half an hour")):
        p["available_minutes"] = min(int(p["available_minutes"]), 30)
    if any(w in t for w in ("more active", "energetic", "workout")):
        p["energy"] = "active"
    elif any(w in t for w in ("relax", "calm", "low energy")):
        p["energy"] = "relaxing"
    return p

def bedrock_explanation(plan, preferences):
    model_id = os.getenv("BEDROCK_MODEL_ID", "").strip()
    if not model_id or not plan:
        return None
    try:
        import boto3
        client = boto3.client("bedrock-runtime", region_name=os.getenv("AWS_REGION", "us-east-1"))
        prompt = (
            "You are Weekend Buddy, a friendly offline activity planner. In two short sentences, "
            "explain why this plan fits. Do not invent places, opening hours, prices, or bookings. "
            f"Budget INR {preferences['budget']}; time {preferences['available_minutes']} minutes; "
            f"style {preferences.get('category', 'either')}; energy {preferences.get('energy', 'any')}; "
            f"activities {[a['name'] for a in plan]}. Costs are estimates."
        )
        response = client.converse(
            modelId=model_id,
            messages=[{"role":"user","content":[{"text":prompt}]}],
            inferenceConfig={"maxTokens":160,"temperature":0.4}
        )
        return response["output"]["message"]["content"][0]["text"].strip()
    except Exception:
        return None

def create_plan(preferences, activities=None):
    activities = activities if activities is not None else load_activities()
    candidates = filter_activities(
        activities, int(preferences["budget"]), int(preferences["available_minutes"]),
        preferences.get("category","either"), preferences.get("energy","any"),
        preferences.get("company","any"), preferences.get("excluded_ids",[])
    )
    plan = build_itinerary(candidates, int(preferences["budget"]), int(preferences["available_minutes"]), int(preferences.get("max_items",4)))
    cost = sum(a["estimated_cost"] for a in plan)
    minutes = sum(a["duration_minutes"] for a in plan)
    explanation = bedrock_explanation(plan, preferences) or (
        "I chose activities that fit your time and budget. Ask me to make the plan cheaper, shorter, more relaxing, or indoors."
        if plan else "No activities matched those exact constraints. Try more time, a higher budget, or choose Any activity style."
    )
    return {"activities":plan,"total_cost":cost,"total_minutes":minutes,
            "remaining_budget":max(0,int(preferences["budget"])-cost),
            "remaining_minutes":max(0,int(preferences["available_minutes"])-minutes),
            "explanation":explanation,"candidate_count":len(candidates)}
