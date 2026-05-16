"""
utils/job_search.py
Fetch top job listings from LinkedIn / Google Jobs via SerpAPI.
"""

import os
import streamlit as st


def search_jobs(job_role: str, skills: list[str] = None, location: str = "India") -> list[dict]:
    """
    Search for top 5 job listings using SerpAPI Google Jobs.
    Returns list of dicts: {title, company, location, link, snippet, posted}
    Requires SERPAPI_KEY in environment.
    """
    api_key = os.getenv("SERPAPI_KEY") or st.secrets.get("SERPAPI_KEY", "")
    if not api_key:
        st.info("💡 SERPAPI_KEY not set. Showing demo job links.")
        return _demo_jobs(job_role)

    try:
        from serpapi import GoogleSearch
        query = job_role
        if skills:
            query += " " + " ".join(skills[:3])

        params = {
            "api_key": api_key,
            "engine": "google_jobs",
            "q": query,
            "location": location,
            "hl": "en",
            "num": 10,
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        jobs = results.get("jobs_results", [])[:5]

        formatted = []
        for job in jobs:
            formatted.append({
                "title": job.get("title", ""),
                "company": job.get("company_name", ""),
                "location": job.get("location", ""),
                "link": _extract_apply_link(job),
                "snippet": job.get("description", "")[:200] + "...",
                "posted": job.get("detected_extensions", {}).get("posted_at", ""),
                "salary": job.get("detected_extensions", {}).get("salary", "Not disclosed"),
            })
        return formatted

    except ImportError:
        st.warning("serpapi not installed. Run: pip install google-search-results")
        return _demo_jobs(job_role)
    except Exception as e:
        st.error(f"Job search error: {e}")
        return _demo_jobs(job_role)


def _extract_apply_link(job: dict) -> str:
    """Get the best apply link from job data."""
    links = job.get("apply_options", [])
    if links:
        # Prefer LinkedIn
        for lnk in links:
            if "linkedin" in lnk.get("link", "").lower():
                return lnk["link"]
        return links[0].get("link", "#")
    return job.get("job_link", "#")


def _demo_jobs(job_role: str) -> list[dict]:
    """Demo job listings when API key is missing."""
    encoded = job_role.replace(" ", "%20")
    linkedin_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded}"
    return [
        {
            "title": f"Senior {job_role}",
            "company": "Demo Corp (add SERPAPI_KEY for real results)",
            "location": "Remote",
            "link": linkedin_url,
            "snippet": f"We are looking for an experienced {job_role} to join our growing team...",
            "posted": "Today",
            "salary": "Not disclosed",
        },
        {
            "title": f"{job_role} – Mid Level",
            "company": "Tech Startup",
            "location": "Bangalore, India",
            "link": linkedin_url,
            "snippet": f"Exciting opportunity for a {job_role} with strong fundamentals...",
            "posted": "2 days ago",
            "salary": "₹8-15 LPA",
        },
        {
            "title": f"Junior {job_role}",
            "company": "Product Company",
            "location": "Hyderabad, India",
            "link": linkedin_url,
            "snippet": f"Great entry-level role for a {job_role} fresher or 0-2 years experience...",
            "posted": "3 days ago",
            "salary": "₹3-6 LPA",
        },
        {
            "title": f"Freelance {job_role}",
            "company": "Various Clients",
            "location": "Remote",
            "link": f"https://www.upwork.com/freelance-jobs/apply/{encoded}/",
            "snippet": f"Multiple freelance {job_role} projects available on contract basis...",
            "posted": "Today",
            "salary": "₹500-2000/hr",
        },
        {
            "title": f"{job_role} Intern",
            "company": "Fortune 500 Company",
            "location": "Mumbai, India",
            "link": linkedin_url,
            "snippet": f"Internship opportunity for students and fresh graduates in {job_role}...",
            "posted": "1 week ago",
            "salary": "₹15,000-25,000/month stipend",
        },
    ]
