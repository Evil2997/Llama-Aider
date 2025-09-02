from tools.aider_yaml_generator.constants import KIB, MIB, GIB


def human_bytes(n: int) -> str:
    if n < KIB:
        return f"{n} B"
    if n < MIB:
        return f"{n / KIB:.1f} KiB"
    if n < GIB:
        return f"{n / MIB:.2f} MiB"
    return f"{n / GIB:.2f} GiB"
