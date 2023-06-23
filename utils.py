import re

def valid_args(q):
    query = q
    if re.findall(r"((^\/|^,|^:|^\.|^[\U0001F600-\U000E007F]).*)", query):
        return False
    if ("https://" or "http://") in query:
        return False
    query = re.sub(r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|gib)(\sme)?)|new|hd|\(|\)|latest|movie|dedo|print|fulllatest|br((o|u)h?)*um(o)*|aya((um(o)*)?|any(one)|with\ssk)*ubtitle(s)?)", "", query.lower(), flags=re.IGNORECASE)
    return query.strip()

def grt(time: float) -> str:
    day = time // (24 * 3600)
    time %= 24 * 3600
    hour = time // 3600
    time %= 3600
    minutes = time // 60
    return f"{day} days, {hour}h:{minutes}m"
