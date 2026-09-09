# Security

Do not open public issues containing:

- MCP bearer tokens
- OAuth tokens
- customer ad account IDs tied to private context
- raw task logs
- backend traces
- database rows
- hidden validation messages

For security issues, email `support@adsagent.md`. Do not include credentials in the first message.

Official website: https://adsagent.md
Official repository: https://github.com/adsagents/adsagent-ai-skills

This repository does not contain the hosted AdsAgent ads MCP implementation or internal schemas. The optional `skill_pack_mcp` stdio server only reads public skill-pack Markdown for Glama/directory preview; it is not an ads backend and must not be given tokens.
