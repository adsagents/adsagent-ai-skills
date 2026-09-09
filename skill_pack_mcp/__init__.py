"""AdsAgent Skill Pack (docs) MCP — public Markdown only, not the hosted ads MCP."""

SERVER_NAME = "AdsAgent Skill Pack (docs)"
SERVER_INSTRUCTIONS = """\
This server is the AdsAgent Skill Pack (docs) MCP. It reads public files from
the adsagent-ai-skills repository (skills/, README.md, VERSION, mcp.json).

It is NOT the hosted AdsAgent Meta, Google Ads, or TikTok MCP. It does not
call ad-platform APIs, execute campaigns, proxy OAuth, or hold credentials.

Use list_skills / get_skill / get_pack_readme to browse documentation.
Use get_hosted_mcp_urls for the real HTTP MCP endpoints; clients must complete
AdsAgent OAuth against those hosted services.
"""
