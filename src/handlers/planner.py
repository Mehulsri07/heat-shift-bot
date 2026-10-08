"""Placeholder so the stack deploys. Owners: A + B (build, save, send plan; daily run)."""


def handler(event: dict, context: object) -> dict:
    print("planner invoked with", event)
    return {"ok": True}
