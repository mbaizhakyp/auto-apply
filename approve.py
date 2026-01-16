import asyncio
import sys
import argparse
from redis.asyncio import Redis
# Fix path
import os
sys.path.append(os.getcwd())
from src.agent.hitl import HITLManager
from dotenv import load_dotenv

load_dotenv()

async def main():
    parser = argparse.ArgumentParser(description="Approve or Reject jobs waiting for HITL.")
    parser.add_argument("job_id", type=int, help="Job ID to approve/reject")
    parser.add_argument("action", choices=["approve", "reject"], help="Action to take")
    
    args = parser.parse_args()
    
    manager = HITLManager()
    
    if args.action == "approve":
        await manager.approve_job(args.job_id)
        print(f"Approved Job {args.job_id}")
    else:
        await manager.reject_job(args.job_id)
        print(f"Rejected Job {args.job_id}")
        
    await manager.redis.aclose()

if __name__ == "__main__":
    asyncio.run(main())
