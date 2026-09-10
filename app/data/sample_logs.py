from typing import Optional

PRESETS = [
    {
        "id": "flare-14",
        "title": "14-day flare escalation",
        "patient": "Synthetic case A",
        "days": 14,
        "teaser": "Remission for five days, then watery stools, knee pain, and a missed dose.",
        "pattern": "Flare",
        "logs": [
            "Felt good. Normal formed stool once. Ate chicken and rice.",
            "No stomach pain. Normal solid bowel movement. Went to the gym.",
            "Felt slightly below par. Bowel was normal. Took my morning azathioprine.",
            "Normal day. Energy levels good. 1 solid stool. Ate some spicy Thai curry.",
            "Felt fine, slight bloating in evening after dinner. Stool was Bristol 4.",
            "Woke up with mild cramps. Stool was mushy twice. Skipped evening medication by mistake.",
            "Mild pain continued, 2 loose watery stools. Feeling worn out.",
            "Knee joints started aching badly. Stool loose 3 times. Felt fatigued.",
            "Had a small mouth ulcer appear. 3 watery stools, moderate lower right quadrant pain.",
            "Struggling with fatigue. Moderate cramping. 4 liquid stools. Left knee swollen.",
            "Severe abdominal cramping around 3pm. 4 watery stools. Poor energy.",
            "Terrible day. Exhausted. 5 watery diarrhea episodes. Severe cramping.",
            "Knee still painful, mouth ulcer hurting. 4 loose stools, severe pain. Took pain relief.",
            "Severe cramps before every bowel movement. 5 liquid stools. Felt terrible all day.",
        ],
    },
    {
        "id": "remission-10",
        "title": "Stable remission",
        "patient": "Synthetic case B",
        "days": 10,
        "teaser": "Formed stools, gym days, and confirmed azathioprine throughout.",
        "pattern": "Remission",
        "logs": [
            "Woke feeling well. One Bristol 4 stool in the morning. Took azathioprine with breakfast. Walked 40 minutes.",
            "Energy normal. No abdominal pain. Solid stool once after lunch. Chicken, rice, steamed broccoli.",
            "Slept through the night. Formed bowel movement, no urgency. Took morning and evening meds as prescribed.",
            "Slightly busy workday but gut quiet. One formed stool. Yoghurt and oats for breakfast. Gym in the evening.",
            "Felt very well. No bloating. Bristol 3–4 once. Confirmed azathioprine taken. Early night.",
            "Weekend hike. No cramping. One solid stool before leaving. Packed rice cakes and banana. Meds taken.",
            "Mild wind after a larger dinner, otherwise fine. Formed stool once. No blood, no mucus. Azathioprine taken.",
            "Normal energy. Bowel habit unchanged — one formed stool. Took medication on time. Read before bed.",
            "Felt well. No joint pain, no mouth ulcers. Solid stool once. Salmon and potatoes. Meds confirmed.",
            "Quiet Sunday. One Bristol 4 stool. No pain. Azathioprine taken morning and evening. Sleeping well.",
        ],
    },
    {
        "id": "recovery-12",
        "title": "Post-flare recovery",
        "patient": "Synthetic case C",
        "days": 12,
        "teaser": "Starts in a moderate flare and steadily settles back toward baseline.",
        "pattern": "Recovery",
        "logs": [
            "Rough start. Moderate right-sided cramps. 4 watery stools. Fatigued. Took steroids as prescribed plus azathioprine.",
            "Still poor energy. 3 liquid stools and mild joint ache in the left knee. Medication taken. Ate plain rice and soup.",
            "Cramps less sharp than yesterday. 3 loose stools, one still watery. Mouth ulcer smaller. All meds taken.",
            "Slept better. 2 mushy stools, less urgency. Knee ache fading. Took morning azathioprine and taper dose.",
            "Energy picking up. One loose stool and one formed. Mild bloating after lunch. Meds taken on time.",
            "Felt below par rather than terrible. One Bristol 5 stool, no overnight waking. Joints quiet. Meds confirmed.",
            "Worked a half day. One formed stool, one soft. No cramping at rest. Finished the steroid taper as instructed.",
            "Almost a normal day. One Bristol 4 stool. Residual tiredness only. Azathioprine taken. Walked 20 minutes.",
            "Felt well aside from slight afternoon fatigue. Formed stool once. No ulcers, no joint pain. Meds taken.",
            "Gym for the first time in two weeks. One solid stool. No pain during exercise. Azathioprine confirmed.",
            "Quiet gut. Bristol 4 once. Appetite back. Chicken, rice, courgette. All doses taken.",
            "Felt very well. One formed stool. No complications. Sleeping through. Medication adherence complete.",
        ],
    },
    {
        "id": "mild-10",
        "title": "Smouldering mild activity",
        "patient": "Synthetic case D",
        "days": 10,
        "teaser": "Never fully well: extra stools, skipped doses, and a dietary trigger.",
        "pattern": "Mild activity",
        "logs": [
            "Slightly below par. One formed stool and one loose. No real pain. Took azathioprine.",
            "Mild lower abdominal ache in the afternoon. Two soft stools. Forgot the evening dose until late, then took it.",
            "Energy low after a late night. Two loose stools, Bristol 5–6. No blood. Morning meds taken.",
            "Felt okay in the morning, worn out by 4pm. One watery stool after a creamy pasta lunch. Azathioprine taken.",
            "Mild cramps before breakfast. Two mushy stools. Small mouth ulcer noticed. Took all medication.",
            "Skipped morning azathioprine in a rush; took it at lunch. One liquid stool, one formed. Joints a bit stiff.",
            "Weekend takeaway — spicy chicken. That evening, two watery stools and moderate cramping. Meds taken.",
            "Still slightly below par. One loose stool. Mouth ulcer lingering. Confirmed both doses today.",
            "Work meeting all day. Two soft stools, urgency once on the train. Mild pain. Azathioprine taken.",
            "Not terrible, not well. One Bristol 6 stool and one formed. Residual fatigue. Evening dose taken on time.",
        ],
    },
]


def get_preset(preset_id: str) -> Optional[dict]:
    for preset in PRESETS:
        if preset["id"] == preset_id:
            return preset
    return None


def preset_summaries() -> list[dict]:
    return [
        {
            "id": p["id"],
            "title": p["title"],
            "patient": p["patient"],
            "days": p["days"],
            "teaser": p["teaser"],
            "pattern": p["pattern"],
            "preview": p["logs"][:3],
        }
        for p in PRESETS
    ]
