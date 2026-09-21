import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.getenv('MONGO_CONNECTION_STRING'))
    db = client[os.getenv('MONGO_DATABASE_NAME', 'job_assistant_db')]
    
    # Check profile for PDF
    profile = await db.profiles.find_one()
    if profile:
        has_pdf = 'original_pdf_base64' in profile and profile['original_pdf_base64']
        pdf_size = len(profile.get('original_pdf_base64', '') or '') if has_pdf else 0
        print(f'Profile has PDF: {has_pdf}, Size: {pdf_size} chars')
    
    # Check optimized resumes
    opt_resumes = await db.optimized_resumes.find().to_list(5)
    print(f'Optimized resumes: {len(opt_resumes)}')
    for r in opt_resumes:
        has_opt_pdf = 'optimized_pdf_base64' in r and r['optimized_pdf_base64']
        opt_pdf_size = len(r.get('optimized_pdf_base64', '') or '') if has_opt_pdf else 0
        print(f'  Resume {str(r["_id"])[:10]}: Has optimized PDF: {has_opt_pdf}, Size: {opt_pdf_size}')
    
    # Check jobs with low scores
    low_jobs = await db.jobs.find({'match_score': {'$lt': 50}}).to_list(5)
    print(f'Jobs with score < 50: {len(low_jobs)}')
    
    all_jobs = await db.jobs.count_documents({})
    print(f'Total jobs: {all_jobs}')
    
    # Get score distribution
    pipeline = [
        {'$group': {'_id': {'$floor': {'$divide': ['$match_score', 10]}}, 'count': {'$sum': 1}}},
        {'$sort': {'_id': 1}}
    ]
    dist = await db.jobs.aggregate(pipeline).to_list(20)
    print('Score distribution (by 10s):')
    for d in dist:
        score_range = f"{int(d['_id'] or 0)*10}-{int(d['_id'] or 0)*10+9}%"
        print(f'  {score_range}: {d["count"]} jobs')

asyncio.run(check())
