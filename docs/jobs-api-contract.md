# Jobs API contract

The dashboard reads `GET {apiBaseUrl}/jobs`; configure the URL in `site/config.js`. With an empty URL it loads fictional `site/sample-jobs.json`.

The response contains `updated_at` and `jobs`. Each job includes `id`, title, company, role, seniority, location, `vietnam_eligible`, `discovered_at`, URL, skills and analysis.

Every analysis preserves the product value chain: `job requirement → candidate gap → learning resource → proof to build`. Required fields are `readiness_score`, recommendation, summary, decision, matched requirements, gaps and roadmap. Each gap contains why it matters, one course, one authoritative document and one proof artifact.

The API must allow the GitHub Pages origin through CORS. Collected jobs remain outside this repository.
