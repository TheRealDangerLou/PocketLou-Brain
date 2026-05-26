"""ACTIVE_LISTEN — Absorb and coach passively. Minimal responses."""


class ActiveListenMode:
    name = "ACTIVE_LISTEN"
    description = "Absorb everything, coach passively, respond minimally"
    temperature = 0.6
    max_tokens = 200
    prefer_local = True
    haptic_on_switch = "mode_switch"
