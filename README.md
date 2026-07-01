# Immigration Tracker

KOS Academic Website + Local Agent for NZ Green List ICT Job Tracking, German PhD Scanning, and Global Immigration Policy Monitoring.

- **SEEK NZ**: Daily scan from QQ Mail, scored against Green List Tier1 ICT
- **German PhD**: EURAXESS + academics.de aggregation
- **Policy Tracker**: OECD skilled immigration policy monitoring
- **Auto Deploy**: GitHub Actions builds KOS and deploys to Pages

## Repository Structure

`
.
├── .github/workflows/deploy.yml
├── local_agent/           # Python local agent
│   ├── seek_email_agent.py
│   ├── git_pusher.py
│   └── ...
├── kos/                   # Next.js academic website
├── data/                  # Agent output (JSON feeds)
└── reports/               # Markdown scan reports
`

## Deployment

https://JRWang2026.github.io/immigration-tracker