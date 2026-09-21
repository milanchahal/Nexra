# backend/app/discovery/platforms/latam_scrapers.py
"""
LATAM/Brazil Focused Scrapers (14 Platforms)
These platforms focus on Latin America and Brazil remote jobs.
"""
import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/121.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7",
}


def create_job(title: str, company: str, location: str, source: str, url: str = "", description: str = "") -> Dict:
    return {
        "job_title": str(title)[:150].strip(),
        "company_name": str(company)[:100].strip() or "Unknown",
        "location": str(location)[:80].strip() or "Remote LATAM",
        "source": source,
        "source_url": url,
        "job_description": description[:3000] if description else f"{title} at {company} - Remote via {source}",
        "posted_date": str(datetime.now().date()),
    }


async def fetch_page(url: str, timeout: int = 25) -> BeautifulSoup:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=HEADERS)
            if response.status_code == 200:
                return BeautifulSoup(response.text, "html.parser")
    except:
        pass
    return None


# =============================================================================
# 1. REVELO
# =============================================================================
async def scrape_revelo() -> List[Dict]:
    """Revelo - LATAM tech talent"""
    jobs = []
    soup = await fetch_page("https://www.revelo.com/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article, [class*="position"]')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Revelo",
                        location="Remote LATAM",
                        source="revelo",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Revelo: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Revelo: Failed to fetch")
    
    return jobs


# =============================================================================
# 2. GEEKHUNTER (Brazil)
# =============================================================================
async def scrape_geekhunter() -> List[Dict]:
    """GeekHunter - Brazil tech jobs"""
    jobs = []
    soup = await fetch_page("https://www.geekhunter.com.br/vagas?remote=true")
    
    if soup:
        for card in soup.select('[class*="vaga"], [class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and ('empresa' in str(x).lower() or 'company' in str(x).lower()))
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "GeekHunter",
                        location="Remote Brazil",
                        source="geekhunter",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ GeekHunter: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ GeekHunter: Failed to fetch")
    
    return jobs


# =============================================================================
# 3. PROGRAMATHOR (Brazil)
# =============================================================================
async def scrape_programathor() -> List[Dict]:
    """Programathor - Brazil dev jobs"""
    jobs = []
    soup = await fetch_page("https://programathor.com.br/jobs-remote")
    
    if soup:
        for card in soup.select('[class*="job"], article, .card')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Programathor",
                        location="Remote Brazil",
                        source="programathor",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Programathor: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Programathor: Failed to fetch")
    
    return jobs


# =============================================================================
# 4. SEUJOB.TECH (Brazil)
# =============================================================================
async def scrape_seujob() -> List[Dict]:
    """SeuJob.tech - Brazil remote"""
    jobs = []
    soup = await fetch_page("https://seujob.tech/remoto")
    
    if soup:
        for card in soup.select('[class*="job"], article, .vaga')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company="SeuJob Company",
                        location="Remote Brazil",
                        source="seujob",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ SeuJob: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ SeuJob: Failed to fetch")
    
    return jobs


# =============================================================================
# 5. COODESH (Brazil)
# =============================================================================
async def scrape_coodesh() -> List[Dict]:
    """Coodesh - Brazil remote dev"""
    jobs = []
    soup = await fetch_page("https://coodesh.com/vagas?remoto=true")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="vaga"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            company_el = card.find(class_=lambda x: x and 'company' in str(x).lower())
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else "Coodesh",
                        location="Remote Brazil",
                        source="coodesh",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Coodesh: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Coodesh: Failed to fetch")
    
    return jobs


# =============================================================================
# 6. IMPULSO (LATAM)
# =============================================================================
async def scrape_impulso() -> List[Dict]:
    """Impulso - LATAM remote"""
    jobs = []
    soup = await fetch_page("https://impulso.network/oportunidades")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="oportunidade"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company="Impulso Network",
                        location="Remote LATAM",
                        source="impulso",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Impulso: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Impulso: Failed to fetch")
    
    return jobs


# =============================================================================
# 7. TECLA (LATAM)
# =============================================================================
async def scrape_tecla() -> List[Dict]:
    """Tecla - LATAM jobs for US companies"""
    jobs = []
    soup = await fetch_page("https://www.tecla.io/join")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="position"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    link = card.find('a', href=True)
                    jobs.append(create_job(
                        title=title,
                        company="Tecla Client",
                        location="Remote LATAM",
                        source="tecla",
                        url=link['href'] if link else ""
                    ))
        
        print(f"   ✅ Tecla: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Tecla: Failed to fetch")
    
    return jobs


# =============================================================================
# 8. BEON.TECH
# =============================================================================
async def scrape_beontech() -> List[Dict]:
    """Beon.Tech remote jobs"""
    jobs = []
    soup = await fetch_page("https://beon.tech/remote-jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Beon.Tech",
                        location="Remote",
                        source="beontech"
                    ))
        
        print(f"   ✅ Beon.Tech: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Beon.Tech: Failed to fetch")
    
    return jobs


# =============================================================================
# 9. FLATWORLD
# =============================================================================
async def scrape_flatworld() -> List[Dict]:
    """Flatworld jobs"""
    jobs = []
    soup = await fetch_page("https://flatworld.co/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Flatworld",
                        location="Remote",
                        source="flatworld"
                    ))
        
        print(f"   ✅ Flatworld: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Flatworld: Failed to fetch")
    
    return jobs


# =============================================================================
# 10. NIXA
# =============================================================================
async def scrape_nixa() -> List[Dict]:
    """Nixa developer jobs"""
    jobs = []
    soup = await fetch_page("https://www.nixa.io/developer-jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Nixa",
                        location="Remote",
                        source="nixa"
                    ))
        
        print(f"   ✅ Nixa: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Nixa: Failed to fetch")
    
    return jobs


# =============================================================================
# 11. INSQUAD
# =============================================================================
async def scrape_insquad() -> List[Dict]:
    """Insquad remote jobs"""
    jobs = []
    soup = await fetch_page("https://insquad.com/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Insquad",
                        location="Remote",
                        source="insquad"
                    ))
        
        print(f"   ✅ Insquad: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Insquad: Failed to fetch")
    
    return jobs


# =============================================================================
# 12. DISTRO
# =============================================================================
async def scrape_distro() -> List[Dict]:
    """Distro remote jobs"""
    jobs = []
    soup = await fetch_page("https://distro.dev/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Distro",
                        location="Remote",
                        source="distro"
                    ))
        
        print(f"   ✅ Distro: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Distro: Failed to fetch")
    
    return jobs


# =============================================================================
# 13. LOKA
# =============================================================================
async def scrape_loka() -> List[Dict]:
    """Loka careers"""
    jobs = []
    soup = await fetch_page("https://loka.com/careers")
    
    if soup:
        for card in soup.select('[class*="job"], [class*="position"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Loka",
                        location="Remote",
                        source="loka"
                    ))
        
        print(f"   ✅ Loka: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Loka: Failed to fetch")
    
    return jobs


# =============================================================================
# 14. KULA
# =============================================================================
async def scrape_kula() -> List[Dict]:
    """Kula jobs"""
    jobs = []
    soup = await fetch_page("https://www.kula.io/jobs")
    
    if soup:
        for card in soup.select('[class*="job"], article')[:25]:
            title_el = card.find(['h2', 'h3', 'h4', 'a'])
            
            if title_el:
                title = title_el.get_text(strip=True)
                if len(title) > 5:
                    jobs.append(create_job(
                        title=title,
                        company="Kula",
                        location="Remote",
                        source="kula"
                    ))
        
        print(f"   ✅ Kula: {len(jobs)} jobs")
    else:
        print(f"   ⚠️ Kula: Failed to fetch")
    
    return jobs


# =============================================================================
# MAIN FUNCTION
# =============================================================================
async def scrape_all_latam_platforms() -> List[Dict]:
    """Run all LATAM scrapers"""
    print("\n🌎 Scraping LATAM platforms...")
    
    batch1 = await asyncio.gather(
        scrape_revelo(),
        scrape_geekhunter(),
        scrape_programathor(),
        scrape_seujob(),
        scrape_coodesh(),
        return_exceptions=True
    )
    
    await asyncio.sleep(1)
    
    batch2 = await asyncio.gather(
        scrape_impulso(),
        scrape_tecla(),
        scrape_beontech(),
        scrape_flatworld(),
        scrape_nixa(),
        return_exceptions=True
    )
    
    await asyncio.sleep(1)
    
    batch3 = await asyncio.gather(
        scrape_insquad(),
        scrape_distro(),
        scrape_loka(),
        scrape_kula(),
        return_exceptions=True
    )
    
    all_jobs = []
    for batch in [batch1, batch2, batch3]:
        for result in batch:
            if isinstance(result, list):
                all_jobs.extend(result)
    
    print(f"   📊 LATAM Platforms Total: {len(all_jobs)} jobs\n")
    return all_jobs


if __name__ == "__main__":
    jobs = asyncio.run(scrape_all_latam_platforms())
    print(f"\nTotal: {len(jobs)} jobs")
