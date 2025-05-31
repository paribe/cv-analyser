cd /home/paribe/cv-analyser/analyze
python3 -c "
from database import AnalyzeDatabase
db = AnalyzeDatabase()
jobs = db.jobs.all()
print(f'Total de vagas: {len(jobs)}')
for job in jobs:
    print(f'- {job.get(\"name\", \"Sem nome\")}')
"