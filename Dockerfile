# AdsAgent Skill Pack (docs) MCP — stdio only.
# This image is NOT the hosted AdsAgent Meta / Google Ads / TikTok backend.
FROM python:3.12-slim-bookworm

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" --uid 1000 app

COPY skill_pack_mcp/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
    && rm -f /tmp/requirements.txt

COPY --chown=app:app skill_pack_mcp /app/skill_pack_mcp
COPY --chown=app:app skills /app/skills
COPY --chown=app:app README.md VERSION mcp.json LICENSE NOTICE.md /app/

USER app

# Glama wraps this stdio process; do not switch to HTTP here.
# /app is the image workdir that holds skills/, VERSION, and mcp.json.
CMD ["python", "-m", "skill_pack_mcp", "--root", "/app"]
