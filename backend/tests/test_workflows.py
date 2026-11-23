from types import SimpleNamespace
import pytest
from backend.automation.policy import validate_apply_url, profile_value, readiness
from backend.services.retrieval import retrieve_passages
from backend.models.application import ApplicationStatus
from backend.schemas.application import ApplicationStartRequest

@pytest.mark.parametrize('url',['http://example.com','https://localhost/a','https://127.0.0.1/a','https://10.0.0.5/a','file:///etc/passwd','https://user:pass@example.com'])
def test_private_application_destinations_rejected(url):
    with pytest.raises(ValueError):validate_apply_url(url)

def test_public_application_url():
    assert validate_apply_url('https://jobs.example.com/apply')=='https://jobs.example.com/apply'

@pytest.mark.parametrize('field,expected',[('full name','Jash Kumar'),('first name','Jash'),('last name','Kumar'),('email','jash@example.com'),('github','https://github.com/example'),('phone',None),('years of experience',None)])
def test_profile_mapping_uses_actual_values(field,expected):
    user=SimpleNamespace(name='Jash Kumar',email='jash@example.com',github_link='https://github.com/example',phone=None)
    assert profile_value(field,user)==expected

def test_preflight_missing_profile():
    result=readiness(SimpleNamespace(name='',email='x@example.com'),None,SimpleNamespace(apply_url=None,url='https://example.com'))
    assert not result['ready'] and len(result['issues'])==2

def test_retrieval_returns_traceable_evidence():
    result=retrieve_passages('Built React dashboards for inventory teams. Reduced errors by 30 percent.','React dashboards')
    assert result and result[0]['source']=='resume:passage-1'
    assert 'React' in result[0]['text']
    assert retrieve_passages('Python data work','unrelated')==[]

def test_application_mode_and_dry_run_state():
    assert ApplicationStatus.DRY_RUN_COMPLETE != ApplicationStatus.SUBMITTED
    with pytest.raises(ValueError):ApplicationStartRequest(mode='anything')
