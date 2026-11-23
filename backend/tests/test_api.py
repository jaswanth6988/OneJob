import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from beanie import init_beanie
from mongomock_motor import AsyncMongoMockClient
from datetime import datetime, timedelta, timezone
from backend.main import app
from backend.models.user import UserProfile
from backend.models.job import JobPosting
from backend.models.resume import Resume
from backend.models.application import JobApplication
from backend.models.manual_review import ManualReviewItem
from backend.models.ai_event import AIEventLog

@pytest_asyncio.fixture
async def client():
    await init_beanie(database=AsyncMongoMockClient().test,document_models=[UserProfile,JobPosting,Resume,JobApplication,ManualReviewItem,AIEventLog])
    async with AsyncClient(transport=ASGITransport(app=app),base_url='http://test') as c:
        yield c

async def account(c,email='one@example.com'):
    r=await c.post('/api/auth/register',json={'email':email,'password':'Testing123!','name':'Test User'})
    assert r.status_code==200,r.text
    r=await c.post('/api/auth/login',data={'username':email,'password':'Testing123!'})
    assert r.status_code==200,r.text
    return {'Authorization':'Bearer '+r.json()['access_token']}

async def seed():
    now=datetime.now(timezone.utc)
    rows=[dict(title='React Developer',company='Acme',location='Bengaluru',remote_type='REMOTE',skills_required=['React','Python'],salary_range='INR 8–12 LPA',seniority_level='Junior',industry='Software'),dict(title='Python Engineer',company='Beta',location='Hyderabad',remote_type='HYBRID',skills_required=['Python'],discovered_at=now-timedelta(days=10)),dict(title='C++ Developer',company='Gamma',location='Bengaluru',skills_required=['C++']),dict(title='Expired React',company='Acme',expires_at=now-timedelta(days=1))]
    jobs=[]
    for i,row in enumerate(rows):
        job=JobPosting(source_name='TestSource',source_job_id=str(i),description='A real test description',url='https://example.com/job',**row)
        await job.insert();jobs.append(job)
    return jobs

@pytest.mark.asyncio
async def test_auth_and_isolation(client):
    assert (await client.get('/api/jobs')).status_code==401
    assert (await client.get('/api/jobs',headers={'Authorization':'Bearer bad'})).status_code==401
    h=await account(client)
    assert (await client.get('/api/auth/me',headers=h)).json()['data']['email']=='one@example.com'
    assert (await client.post('/api/auth/login',data={'username':'one@example.com','password':'wrong'})).status_code==400
    jobs=await seed();id=str(jobs[0].id)
    assert (await client.put(f'/api/jobs/{id}/save',headers=h)).status_code==200
    await client.put(f'/api/jobs/{id}/save',headers=h)
    assert (await client.get('/api/jobs?saved=true',headers=h)).json()['data']['total']==1
    other=await account(client,'two@example.com')
    assert (await client.get('/api/jobs?saved=true',headers=other)).json()['data']['total']==0
    await client.delete(f'/api/jobs/{id}/save',headers=h)
    assert (await client.get('/api/jobs?saved=true',headers=h)).json()['data']['total']==0

@pytest.mark.asyncio
@pytest.mark.parametrize('query,count',[
 ('',3),('search=React',1),('search=React%20Acme',1),('search=C%2B%2B',1),('search=.*',0),
 ('location=Bengaluru',2),('remote_type=REMOTE&location=Bengaluru&skills=React,Python',1),
 ('remote_type=HYBRID&skills=React',0),('company=Acme&salary_only=true',1),('salary_only=true',1),
 ('posted_days=3',2),('seniority=Junior',1),('industry=Software',1),('source=missing',0),('include_expired=true',4)])
async def test_filters(client,query,count):
    h=await account(client);await seed()
    r=await client.get('/api/jobs?'+query,headers=h)
    assert r.status_code==200,r.text
    assert r.json()['data']['total']==count

@pytest.mark.asyncio
async def test_pagination_validation_facets(client):
    h=await account(client);await seed()
    a=(await client.get('/api/jobs?page_size=2&page=1&sort_by=company',headers=h)).json()['data']
    b=(await client.get('/api/jobs?page_size=2&page=2&sort_by=company',headers=h)).json()['data']
    assert a['pages']==2 and a['total']==3 and len(b['items'])==1
    assert {x['_id'] for x in a['items']}.isdisjoint({x['_id'] for x in b['items']})
    for q in ['page=0','page_size=101','posted_days=-1','min_score=101','sort_by=garbage']:
        assert (await client.get('/api/jobs?'+q,headers=h)).status_code==422
    assert (await client.get('/api/jobs/facets',headers=h)).json()['data']['sources']==['TestSource']
    assert (await client.put('/api/jobs/bad/save',headers=h)).status_code==404

@pytest.mark.asyncio
async def test_resume_ownership(client):
    h=await account(client);user=await UserProfile.find_one({'email':'one@example.com'})
    r=Resume(user_id=user,title='Private',version_name='v1',file_path='/tmp/no-file',original_filename='x.pdf',file_type='pdf')
    await r.insert();other=await account(client,'two@example.com')
    assert (await client.get(f'/api/resumes/{r.id}',headers=h)).status_code==200
    assert (await client.get(f'/api/resumes/{r.id}',headers=other)).status_code==404
    assert (await client.get(f'/api/resumes/{r.id}/download',headers=other)).status_code==404
    assert (await client.get('/storage/demo_resume.pdf')).status_code==404

@pytest.mark.asyncio
async def test_personal_scores_and_refresh(client):
    h=await account(client);user=await UserProfile.find_one({'email':'one@example.com'});jobs=await seed()
    await jobs[0].update({'$set':{f'user_matches.{user.id}':{'score':92,'status':'MATCHED','match_result':{'reason':'Test'}}}})
    assert (await client.get('/api/jobs?min_score=90',headers=h)).json()['data']['total']==1
    other=await account(client,'other@example.com')
    assert (await client.get('/api/jobs?min_score=85',headers=other)).json()['data']['total']==0
    login=(await client.post('/api/auth/login',data={'username':'one@example.com','password':'Testing123!'})).json()
    assert (await client.post('/api/auth/refresh',json={'refresh_token':login['refresh_token']})).status_code==200
    assert (await client.post('/api/auth/refresh',json={'refresh_token':login['access_token']})).status_code==401

def test_ratings_do_not_fabricate():
    from backend.services.resume_rating import rate_resume
    from backend.services.interview_coach import interview_coach
    from backend.services.resume_tailor import resume_tailor
    assert rate_resume('',[])['score']==0
    with pytest.raises(ValueError): interview_coach._fallback_evaluation('A long answer '*100)
    with pytest.raises(ValueError): resume_tailor._fallback_response(None,None)

@pytest.mark.asyncio
async def test_profile_fields_persist_and_preflight(client):
    h=await account(client);jobs=await seed()
    response=await client.put('/api/preferences',headers=h,json={'name':'Real Name','phone':'12345','location':'Bengaluru'})
    assert response.status_code==200
    prefs=(await client.get('/api/preferences',headers=h)).json()['data']
    assert prefs['name']=='Real Name' and prefs['phone']=='12345'
    check=(await client.get(f'/api/applications/preflight/{jobs[0].id}',headers=h)).json()['data']
    assert not check['ready'] and 'resume' in ' '.join(check['issues'])
    assert (await client.post(f'/api/applications/start/{jobs[0].id}',headers=h,json={'mode':'INVALID'})).status_code==422
