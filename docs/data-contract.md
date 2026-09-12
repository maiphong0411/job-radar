# Private job data contract

Job data is deliberately excluded from Git. Pass the CSV path to the CLI at runtime.

Supported columns:

| Canonical field | Accepted aliases | Required |
| --- | --- | --- |
| `title` | `job_title` | Yes |
| `company` | `company_name` | Yes |
| `location` | `job_location` | Yes |
| `description` | `job_description` | Recommended |
| `url` | `job_url`, `source_url` | Yes |
| `eligibility_evidence` | — | Recommended |
| `status` | — | No; defaults to `new` |

Rows whose status is `closed` are excluded from the shortlist. CSV files, `data/`, and generated `output/` are ignored by Git.
