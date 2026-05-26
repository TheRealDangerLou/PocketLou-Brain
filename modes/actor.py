"""ACTOR — Script, audition, character, casting. Lou is working."""


class ActorMode:
    name = "ACTOR"
    description = "Script analysis, character work, audition strategy"
    temperature = 0.8
    max_tokens = 1200
    prefer_local = True
    haptic_on_switch = "mode_switch"

    active_projects = [
        "The Broken Oath — historical drama, 1700s–1800s Great Lakes",
        "The Last Fix — TV concept, protagonist Armstrong, sobriety journey",
        "Actor's Companion — mobile rehearsal/audition app (Lou is dev + user)",
    ]
