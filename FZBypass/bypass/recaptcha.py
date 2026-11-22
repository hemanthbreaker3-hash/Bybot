from re import findall
from FZBypass.core.exceptions import DDLException
from FZBypass.core.http_client import get_http_session


async def recaptchaV3(
    ANCHOR_URL="https://www.google.com/recaptcha/api2/anchor?ar=1&k=6Lcr1ncUAAAAAH3cghg6cOTPGARa8adOf-y9zv2x&co=aHR0cHM6Ly9vdW8ucHJlc3M6NDQz&hl=en&v=pCoGBhjs9s8EhFOHJFe8cqis&size=invisible&cb=ahgyd1gkfkhe",
):
    matches = findall(r"(api2|enterprise)/anchor\?(.*)", ANCHOR_URL)
    if not matches:
        raise DDLException("Invalid reCAPTCHA Anchor URL")
    api_type, raw_params = matches[0]
    url_base = f"https://www.google.com/recaptcha/{api_type}/"
    params = dict(pair.split("=", 1) for pair in raw_params.split("&") if "=" in pair)

    session = await get_http_session()
    headers = {"content-type": "application/x-www-form-urlencoded"}

    async with session.get(f"{url_base}anchor?{raw_params}", headers=headers) as res:
        anchor_text = await res.text()

    tokens = findall(r'"recaptcha-token" value="(.*?)"', anchor_text)
    if not tokens:
        raise DDLException("reCAPTCHA token extraction failed")

    payload = (
        f"v={params.get('v', '')}&reason=q&c={tokens[0]}"
        f"&k={params.get('k', '')}&co={params.get('co', '')}"
    )
    async with session.post(
        f"{url_base}reload",
        params={"k": params.get("k", "")},
        data=payload,
        headers=headers,
    ) as res:
        reload_text = await res.text()

    rresp = findall(r'"rresp","(.*?)"', reload_text)
    if not rresp:
        raise DDLException("reCAPTCHA reload response failed")
    return rresp[0]
