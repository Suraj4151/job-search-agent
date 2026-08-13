# Daily Job Search Agent

This repo runs a daily agent that scrapes company career pages, matches jobs to resumes, appends results to a Google Sheet, and emails top matches.

## Files
- job_agent.py
- .github/workflows/daily_job_agent.yml
- Consolidated_Corporate_Directory_v2.xlsx

## Setup checklist
1. Create Google Cloud project and enable Sheets and Drive APIs.
2. Create a service account, grant Editor on the target Google Sheet, and download JSON key.
3. Create a Google Sheet and share with the service account email.
4. Create a Gmail account app password for SMTP (or use SMTP relay).
5. Create a GitHub repo and push these files.
6. Add GitHub Secrets:
   - GCP_SERVICE_ACCOUNT_JSON (paste entire JSON)
   - SHEET_ID (Google Sheet ID)
   - EMAIL_USER (myjobsearchagent@gmail.com)
   - EMAIL_PASSWORD (app password)
   - EMAIL_TO (optional; defaults to EMAIL_USER)
7. Enable GitHub Actions. Trigger workflow manually to test.

## Notes
- Some career sites require JavaScript; if results are missing, we can add Selenium.
- Tune scoring thresholds in job_agent.py after reviewing initial results.
