import asyncio
import os
from app.core.config import settings
from app.core.db import connect_to_mongo, get_database_client

async def clear_old_jobs():
    await connect_to_mongo()
    db = get_database_client()
    jobs_collection = db[settings.MONGO_DATABASE_NAME].get_collection('jobs')
    
    # List of old/generic sources to remove
    sources_to_remove = [
        'linkedin',
        'indeed',
        'glassdoor',
        'jobspy', 
        'naukri',
        'generic_board',
        'google',
        'ziprecruiter'
    ]
    
    print("Checking current job distribution...")
    pipeline = [{'$group': {'_id': '$source', 'count': {'$sum': 1}}}]
    stats = await jobs_collection.aggregate(pipeline).to_list(None)
    for s in stats:
        print(f"  {s.get('_id', 'Unknown')}: {s.get('count', 0)}")
        
    print(f"\nDeleting jobs from sources: {sources_to_remove}...")
    result = await jobs_collection.delete_many({'source': {'$in': sources_to_remove}})
    
    print(f"\n✅ Deleted {result.deleted_count} old generic jobs.")
    
    # Verify remaining
    count = await jobs_collection.count_documents({})
    print(f"Remaining jobs in DB: {count}")
    
    # Also clear "profiles" if needed or optimized_resumes to force re-match? No, just jobs.

if __name__ == "__main__":
    asyncio.run(clear_old_jobs())
