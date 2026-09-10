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
    {
        "id": "gappy-12",
        "title": "Skipped empty days",
        "patient": "Synthetic case E",
        "days": 4,
        "teaser": "Only writes on bad days. Blank lines, comments, and Day 1 / 5 / 9 / 12 gaps.",
        "pattern": "Stress test",
        "raw": """# I only bother writing when something is wrong. Quiet days are blank on purpose.

Day 1: Felt fine. One formed stool. Took azathioprine.


Day 5: Back after three silent days. Mild cramps, two loose stools. Pretty sure I missed the evening pill on day 3.

Day 9: Did not log 6–8. Weekend was watery like four times, knee puffed up, mouth ulcer. Still skipping the diary when I feel ok.

Day 12: Still rough. Three liquid stools. Forgot the morning dose. Days 10 and 11 were similar so I left them empty.
""",
        "logs": [
            "Felt fine. One formed stool. Took azathioprine.",
            "Back after three silent days. Mild cramps, two loose stools. Pretty sure I missed the evening pill on day 3.",
            "Did not log 6–8. Weekend was watery like four times, knee puffed up, mouth ulcer. Still skipping the diary when I feel ok.",
            "Still rough. Three liquid stools. Forgot the morning dose. Days 10 and 11 were similar so I left them empty.",
        ],
    },
    {
        "id": "informal-14",
        "title": "Very informal texts",
        "patient": "Synthetic case F",
        "days": 14,
        "teaser": "WhatsApp energy: slang, typos, no punctuation, mixed day labels.",
        "pattern": "Stress test",
        "raw": """yo day1 basically fine just a normal poop chicken n rice
day2 nah pain nbd went gym solid bm
day 3 bit meh took my aza whatever
DAY4 spicy thai curry lol hope thats ok 1 solid
d5 bloated after dinner bristol 4ish
day6 woke up crampy mushy x2 skipped the nite pill oops
7 still crampy 2 watery stools knackered tbh
day eight knee is KILLING me rn stool loose 3 times so tired
got a mouth sore like a canker?? 3 watery + lower right hurtin
idk struggling 4 liquid knee swollen like a balloon
3pm cramps were brutal 4 watery no energy
terrible day 5 diarrhea episodes i was dying
knee + ulcer still 4 loose stools took some painkillers
same as yesterday basically 5 liquid felt awful all day didn't even shower""",
        "logs": [
            "yo day1 basically fine just a normal poop chicken n rice",
            "day2 nah pain nbd went gym solid bm",
            "day 3 bit meh took my aza whatever",
            "DAY4 spicy thai curry lol hope thats ok 1 solid",
            "d5 bloated after dinner bristol 4ish",
            "day6 woke up crampy mushy x2 skipped the nite pill oops",
            "7 still crampy 2 watery stools knackered tbh",
            "day eight knee is KILLING me rn stool loose 3 times so tired",
            "got a mouth sore like a canker?? 3 watery + lower right hurtin",
            "idk struggling 4 liquid knee swollen like a balloon",
            "3pm cramps were brutal 4 watery no energy",
            "terrible day 5 diarrhea episodes i was dying",
            "knee + ulcer still 4 loose stools took some painkillers",
            "same as yesterday basically 5 liquid felt awful all day didn't even shower",
        ],
    },
    {
        "id": "terse-8",
        "title": "One-word days",
        "patient": "Synthetic case G",
        "days": 8,
        "teaser": "Almost nothing written. Tests extraction when the note is a fragment.",
        "pattern": "Stress test",
        "raw": """ok
fine
meh. aza
curry. 1 stool
cramps. skipped meds
watery x2. tired
knee. liquid x4. ulcer
dying. 5 diarrhea""",
        "logs": [
            "ok",
            "fine",
            "meh. aza",
            "curry. 1 stool",
            "cramps. skipped meds",
            "watery x2. tired",
            "knee. liquid x4. ulcer",
            "dying. 5 diarrhea",
        ],
    },
    {
        "id": "messy-header",
        "title": "Notes, headers, out of order",
        "patient": "Synthetic case H",
        "days": 7,
        "teaser": "A comment, WEEK ONE header, Day 4 before Day 2, and skipped empty rows.",
        "pattern": "Stress test",
        "raw": """# crohns log export
WEEK ONE
Day 4: watery x3 after the takeaway, forgot aza in the morning
Day 1: all good formed stool took meds
Day 2:

Day 6: mouth ulcer + 4 liquid + knee ache took everything
Day 3: same as usual i guess?? 1 solid
nothing to report really so i left day 5 off
Day 7: terrible 5 watery couldn't work
""",
        "logs": [
            "WEEK ONE",
            "watery x3 after the takeaway, forgot aza in the morning",
            "all good formed stool took meds",
            "mouth ulcer + 4 liquid + knee ache took everything",
            "same as usual i guess?? 1 solid",
            "nothing to report really so i left day 5 off",
            "terrible 5 watery couldn't work",
        ],
    },
]


def _ninety_day_slow_flare() -> list[str]:
    meals = [
        "chicken and rice",
        "oats and yoghurt",
        "tomato soup",
        "plain pasta",
        "spicy Thai curry",
        "toast",
        "salmon and potatoes",
    ]
    logs = []
    for day in range(1, 91):
        meal = meals[day % len(meals)]
        missed = day in {22, 47, 71}
        if day <= 30:
            meds = "Skipped evening azathioprine." if missed else "Took azathioprine as prescribed."
            logs.append(
                f"Quiet gut. Energy decent. One formed Bristol 4 stool. Ate {meal}. {meds} Walked in the evening."
            )
        elif day <= 55:
            liquid = 1 + (day - 31) // 8
            meds = "Forgot the morning dose, took it late." if missed else "Meds taken on time."
            logs.append(
                f"Slightly below par. Mild lower cramps after lunch. {liquid} loose stool(s), not fully watery. "
                f"Ate {meal}. {meds} Sleep a bit broken."
            )
        elif day <= 75:
            liquid = 2 + (day - 56) // 7
            extra = "Left knee aching." if day >= 62 else "No extra-intestinal symptoms."
            meds = "Missed the evening pill." if missed else "Azathioprine taken."
            logs.append(
                f"Poor energy. Moderate right-sided pain. {liquid} watery stools with urgency. {extra} "
                f"Ate {meal}. {meds}"
            )
        else:
            extra = "Mouth ulcer and swollen knee."
            logs.append(
                f"Terrible day. Severe cramping before each bowel movement. {4 + (day % 2)} liquid stools. "
                f"{extra} Barely ate {meal}. Took azathioprine plus simple pain relief. Could not work a full day."
            )
    return logs


def _ninety_day_relapsing() -> list[str]:
    logs = []
    flare_windows = {(40, 52), (70, 82)}

    def in_flare(day: int) -> bool:
        return any(start <= day <= end for start, end in flare_windows)

    for day in range(1, 91):
        missed = day in {41, 73}
        if in_flare(day):
            peak = 5 if day in range(46, 50) or day in range(76, 80) else 3
            logs.append(
                f"Flare day. Moderate to severe cramps. {peak} watery stools. Fatigue heavy. "
                f"{'Skipped azathioprine in the rush.' if missed else 'Took steroids as instructed plus azathioprine.'} "
                f"Plain rice only."
            )
        elif any(start - 5 <= day < start for start, _end in flare_windows):
            logs.append(
                "Turning. Mild pain, two mushy stools, energy dipping. Took all medication. Avoided spice."
            )
        elif any(end < day <= end + 6 for _start, end in flare_windows):
            logs.append(
                "Settling. One loose stool and one formed. Residual tiredness. Azathioprine taken. Knee quieter."
            )
        else:
            logs.append(
                "Remission-range. One formed stool, no pain, gym or a walk. Azathioprine confirmed. Sleeping through."
            )
    return logs


PRESETS += [
    {
        "id": "slow-flare-90",
        "title": "90-day slow flare",
        "patient": "Synthetic case I",
        "days": 90,
        "teaser": "A quiet month, then smouldering activity, then a severe last fortnight.",
        "pattern": "90 days",
        "logs": _ninety_day_slow_flare(),
    },
    {
        "id": "relapsing-90",
        "title": "90-day relapsing course",
        "patient": "Synthetic case J",
        "days": 90,
        "teaser": "Mostly well, with two discrete flares around days 40–52 and 70–82.",
        "pattern": "90 days",
        "logs": _ninety_day_relapsing(),
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
