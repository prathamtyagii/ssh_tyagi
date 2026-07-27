NAME = "Pratham Tyagi"
TITLE = "Software Engineer @ Tower Research Capital"
TAGLINE = "Backend engineer working on trading systems. DTU '24. Competitive programmer on the side."

ABOUT = """\
Hey, I'm Pratham. I'm a software engineer at Tower Research Capital, where I
build backend systems that sit close to trading -- corporate actions
processing, trade cost/incentive pipelines, and data normalization across
brokers and asset classes. Before that, I studied Computer Engineering at
Delhi Technological University.

Outside of work, my life revolves around football, my dear PS5 and a
13.3 inch screen which does wonders(MBA lol). I do a fair bit of competitive 
programming (Codeforces, LeetCode), and I like building things like this 
terminal you're currently sitting in.
"""

EXPERIENCE = [
    {
        "role": "Software Engineer",
        "company": "Tower Research Capital",
        "period": "Aug 2024 -- Present",
        "bullets": [
            "Built an enterprise-grade Corporate Actions module (mergers, spinoffs, "
            "splits, dividends) across Equities and Derivatives in 150+ trading "
            "venues worldwide.",
            "Designed a core engine feeding effective corporate actions from "
            "Bloomberg APIs and correcting real-time front-office positions via a "
            "highly concurrent backend handling 15K+ adjustments weekly.",
            "Developed a normalised parquet driven DuckDB data archive for 15"
            "different heterogeneous data feeds using hive partitioning to make it effecient. "
            "Exposed a MCP Tool over these data feeds to be queryable via NLP.",
            "Primary developer on Transaction Master, enriching 10M+ trades/day "
            "with market and asset-class data into an Elasticsearch cluster via "
            "Kafka; onboarded products spanning US equity ETFs, create/redeem "
            "baskets, NAVX, BTIC, EFP, and equity swaps.",
            "Worked on a JSON-driven framework to normalize broker files across "
            "heterogeneous formats (csv/xlsx/pdf/txt/tsv/xml) for 30+ brokers and "
            "multiple asset classes, used by Ops for trade/position/cash/NAV "
            "reconciliation.",
        ],
    },
    {
        "role": "Core Engineering Intern",
        "company": "Tower Research Capital",
        "period": "Jan 2024 -- Jul 2024",
        "bullets": [
            "Built a new Project Master module end-to-end: database schema, REST "
            "APIs for workflow management, and UI screens.",
            "Built a log-metrics system on a GCP-managed Elasticsearch cluster and "
            "updated the Zuul API Gateway + Eureka service discovery setup to "
            "handle 50K+ requests daily.",
        ],
    },
    {
        "role": "Software Engineering Intern",
        "company": "Tumlare Software (Kuoni Tumlare)",
        "period": "Jun 2023 -- Jul 2023",
        "bullets": [
            "Designed REST APIs for User Management modules in the firm's BIS 2.0 "
            "product using Java Spring/Spring Boot.",
            "Integrated password management and an admin dashboard, automating "
            "what had been manual user modification.",
        ],
    },
]

SKILLS = {
    "Languages": ["Python", "Java", "JavaScript", "SQL"],
    "Frameworks": ["Spring Boot", "FastAPI", "React", "Node.js"],
    "Databases": ["PostgreSQL", "Elasticsearch", "MySQL", "MongoDB"],
    "Competitive Programming": [
        "Codeforces Expert (1600)",
        "LeetCode Knight (1986)",
        "1000+ LeetCode problems solved",
    ],
}

CONTACT = {
    "Email": "prathamtyagi10@gmail.com",
    "GitHub": "https://github.com/prathamtyagii",
    "LinkedIn": "https://www.linkedin.com/in/pratham-tyagi-0804bb1b7/",
    "Codeforces": "https://codeforces.com/profile/prathamtyagii",
    "LeetCode": "https://leetcode.com/prathamtyagii1011/",
    "Website": "https://tyagi.web",
}
