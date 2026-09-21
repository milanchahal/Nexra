# backend/app/discovery/remote_scrapers_part2.py
"""
Part 2: Custom scrapers for platforms 8-47
"""
import asyncio
import httpx
import random
from typing import List, Dict
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/121.0.0.0",
]

def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS), "Accept": "text/html", "Accept-Encoding": "identity"}

async def fetch_and_parse(url: str) -> BeautifulSoup:
    async with httpx.AsyncClient(timeout=25, follow_redirects=True) as c:
        r = await c.get(url, headers=get_headers())
        return BeautifulSoup(r.text, "html.parser") if r.status_code == 200 else None

# 8. FlexJobs
async def scrape_flexjobs() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.flexjobs.com/remote-jobs/computer-it")
        if soup:
            for card in soup.select("[class*='job-title'], [class*='sc-job']")[:15]:
                t = card.get_text(strip=True)
                if len(t) > 5: jobs.append({"job_title": t[:80], "company_name": "FlexJobs", "source": "flexjobs", "location": "Remote"})
    except: pass
    return jobs

# 9. Jobspresso
async def scrape_jobspresso() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://jobspresso.co/remote-work/")
        if soup:
            for a in soup.select("h3.job_listing-title a, .job-title a")[:15]:
                jobs.append({"job_title": a.get_text(strip=True)[:80], "company_name": "Jobspresso", "source": "jobspresso", "source_url": a.get("href",""), "location": "Remote"})
    except: pass
    return jobs

# 10. JS Remotely
async def scrape_jsremotely() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://jsremotely.com/")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "JSRemotely", "source": "jsremotely", "location": "Remote"})
    except: pass
    return jobs

# 11. Hubstaff Talent
async def scrape_hubstaff() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://talent.hubstaff.com/search/jobs")
        if soup:
            for card in soup.select(".job-card, [class*='search-result']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Hubstaff", "source": "hubstaff", "location": "Remote"})
    except: pass
    return jobs

# 12. Nodesk
async def scrape_nodesk() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://nodesk.co/remote-jobs/")
        if soup:
            for a in soup.select("a[href*='/remote-jobs/']")[:15]:
                t = a.get_text(strip=True)
                if len(t) > 5 and len(t) < 100: jobs.append({"job_title": t, "company_name": "Nodesk", "source": "nodesk", "location": "Remote"})
    except: pass
    return jobs

# 13. Pangian
async def scrape_pangian() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://pangian.com/job-travel-remote/")
        if soup:
            for card in soup.select("[class*='job-list'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Pangian", "source": "pangian", "location": "Remote"})
    except: pass
    return jobs

# 14. PowerToFly
async def scrape_powertofly() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://powertofly.com/jobs/")
        if soup:
            for card in soup.select("[class*='job-card'], [class*='JobCard']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "PowerToFly", "source": "powertofly", "location": "Remote"})
    except: pass
    return jobs

# 15. Turing
async def scrape_turing() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.turing.com/remote-developer-jobs")
        if soup:
            for card in soup.select("[class*='job'], [class*='opportunity']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Turing", "source": "turing", "location": "Remote"})
    except: pass
    return jobs

# 16. WellFound
async def scrape_wellfound() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://wellfound.com/role/r/software-engineer")
        if soup:
            for card in soup.select("[class*='job'], [class*='styles_result']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Startup", "source": "wellfound", "location": "Remote"})
    except: pass
    return jobs

# 17. AuthenticJobs
async def scrape_authenticjobs() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://authenticjobs.com/")
        if soup:
            for job in soup.select(".job-listing, [class*='job']")[:15]:
                t = job.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "AuthenticJobs", "source": "authenticjobs", "location": "Remote"})
    except: pass
    return jobs

# 18. Landing.jobs
async def scrape_landing_jobs() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://landing.jobs/jobs?remote=true")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Landing.jobs", "source": "landingjobs", "location": "Remote EU"})
    except: pass
    return jobs

# 19. Remote100K
async def scrape_remote100k() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://remote100k.com/")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Remote100K", "source": "remote100k", "location": "Remote"})
    except: pass
    return jobs

# 20. Levels.fyi Jobs
async def scrape_levelsfyi() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.levels.fyi/jobs")
        if soup:
            for card in soup.select("[class*='job'], [class*='JobCard']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Levels.fyi", "source": "levelsfyi", "location": "Remote"})
    except: pass
    return jobs

# 21. Workatastartup
async def scrape_workatastartup() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.workatastartup.com/")
        if soup:
            for card in soup.select("[class*='job'], [class*='company']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "YC Startup", "source": "workatastartup", "location": "Remote"})
    except: pass
    return jobs

# 22. 4 Day Week
async def scrape_4dayweek() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://4dayweek.io/remote-jobs")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "4DayWeek", "source": "4dayweek", "location": "Remote"})
    except: pass
    return jobs

# 23. SkipTheDrive
async def scrape_skipthedrive() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.skipthedrive.com/")
        if soup:
            for a in soup.select("a[href*='job'], [class*='job-title']")[:15]:
                t = a.get_text(strip=True)
                if len(t) > 5: jobs.append({"job_title": t[:80], "company_name": "SkipTheDrive", "source": "skipthedrive", "location": "Remote"})
    except: pass
    return jobs

# 24. VanHack
async def scrape_vanhack() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://vanhack.com/jobs")
        if soup:
            for card in soup.select("[class*='job'], [class*='position']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "VanHack", "source": "vanhack", "location": "Remote"})
    except: pass
    return jobs

# 25. SnapHunt
async def scrape_snaphunt() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://snaphunt.com/job-listing")
        if soup:
            for card in soup.select("[class*='job'], [class*='listing']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "SnapHunt", "source": "snaphunt", "location": "APAC"})
    except: pass
    return jobs

# 26. TotalJobs
async def scrape_totaljobs() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.totaljobs.com/jobs/remote-software-developer")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "TotalJobs", "source": "totaljobs", "location": "UK Remote"})
    except: pass
    return jobs

# 27. Gun.io
async def scrape_gunio() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://gun.io/find-work/")
        if soup:
            for card in soup.select("[class*='job'], [class*='opportunity']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Gun.io", "source": "gunio", "location": "Remote"})
    except: pass
    return jobs

# 28. Hired
async def scrape_hired() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://hired.com/talent")
        if soup:
            for card in soup.select("[class*='job'], [class*='position']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Hired", "source": "hired", "location": "Remote"})
    except: pass
    return jobs

# 29. Soshace
async def scrape_soshace() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://soshace.com/jobs")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Soshace", "source": "soshace", "location": "Remote"})
    except: pass
    return jobs

# 30. Strider
async def scrape_strider() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.strider.io/")
        if soup:
            for card in soup.select("[class*='job'], [class*='role']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Strider", "source": "strider", "location": "Remote"})
    except: pass
    return jobs

# 31. Tecla
async def scrape_tecla() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.tecla.io/join")
        if soup:
            for card in soup.select("[class*='job'], [class*='position']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Tecla", "source": "tecla", "location": "LATAM"})
    except: pass
    return jobs

# 32. Beon.Tech
async def scrape_beontech() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://beon.tech/remote-jobs")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Beon.Tech", "source": "beontech", "location": "Remote"})
    except: pass
    return jobs

# 33. Flatworld
async def scrape_flatworld() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://flatworld.co/jobs")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Flatworld", "source": "flatworld", "location": "Remote"})
    except: pass
    return jobs

# 34. GeekHunter
async def scrape_geekhunter() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.geekhunter.com.br/vagas")
        if soup:
            for card in soup.select("[class*='job'], [class*='vaga']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "GeekHunter", "source": "geekhunter", "location": "Brazil Remote"})
    except: pass
    return jobs

# 35. Idealist
async def scrape_idealist() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.idealist.org/en/jobs?locationType=REMOTE")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Idealist", "source": "idealist", "location": "Remote"})
    except: pass
    return jobs

# 36. Kula
async def scrape_kula() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.kula.io/jobs")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Kula", "source": "kula", "location": "Remote"})
    except: pass
    return jobs

# 37. Loka
async def scrape_loka() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://loka.com/careers")
        if soup:
            for card in soup.select("[class*='job'], [class*='position']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Loka", "source": "loka", "location": "Remote"})
    except: pass
    return jobs

# 38. Nixa
async def scrape_nixa() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.nixa.io/developer-jobs")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Nixa", "source": "nixa", "location": "Remote"})
    except: pass
    return jobs

# 39. Programathor
async def scrape_programathor() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://programathor.com.br/jobs")
        if soup:
            for card in soup.select("[class*='job'], [class*='vaga']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Programathor", "source": "programathor", "location": "Brazil"})
    except: pass
    return jobs

# 40. Remote.com
async def scrape_remotecom() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://remote.com/jobs/all")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Remote.com", "source": "remotecom", "location": "Remote"})
    except: pass
    return jobs

# 41. RemoteYeah
async def scrape_remoteyeah() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://remoteyeah.com/")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "RemoteYeah", "source": "remoteyeah", "location": "Remote"})
    except: pass
    return jobs

# 42. Revelo
async def scrape_revelo() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://www.revelo.com/jobs")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Revelo", "source": "revelo", "location": "LATAM"})
    except: pass
    return jobs

# 43. SeuJob.tech
async def scrape_seujob() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://seujob.tech/remote")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "SeuJob", "source": "seujob", "location": "Brazil"})
    except: pass
    return jobs

# 44. Coodesh
async def scrape_coodesh() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://coodesh.com/vagas")
        if soup:
            for card in soup.select("[class*='job'], [class*='vaga']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Coodesh", "source": "coodesh", "location": "Brazil"})
    except: pass
    return jobs

# 45. Impulso
async def scrape_impulso() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://impulso.network/oportunidades")
        if soup:
            for card in soup.select("[class*='job'], [class*='oportunidade']")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Impulso", "source": "impulso", "location": "LATAM"})
    except: pass
    return jobs

# 46. Insquad
async def scrape_insquad() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://insquad.com/")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Insquad", "source": "insquad", "location": "Remote"})
    except: pass
    return jobs

# 47. Distro
async def scrape_distro() -> List[Dict]:
    jobs = []
    try:
        soup = await fetch_and_parse("https://distro.dev/")
        if soup:
            for card in soup.select("[class*='job'], article")[:15]:
                t = card.find(["h2","h3","a"])
                if t: jobs.append({"job_title": t.get_text(strip=True)[:80], "company_name": "Distro", "source": "distro", "location": "Remote"})
    except: pass
    return jobs
