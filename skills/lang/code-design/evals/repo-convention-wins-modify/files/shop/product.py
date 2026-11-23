def url(title: str) -> str:
    return "/p/" + "-".join(title.lower().split())


def legacy_name(a, b, c, d, e, f):
    return str(a)+str(b)+str(c)+str(d)+str(e)+str(f)
