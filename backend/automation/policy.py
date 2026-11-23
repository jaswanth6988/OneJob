"""Pure application policies, shared by API preflight and the browser adapter."""
from urllib.parse import urlparse
import ipaddress

def validate_apply_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Application URL must be a public HTTPS URL')
    host = parsed.hostname.lower()
    if host == 'localhost' or host.endswith(('.localhost', '.local', '.internal')):
        raise ValueError('Private application destinations are not supported')
    try:
        if not ipaddress.ip_address(host).is_global:
            raise ValueError('Private application destinations are not supported')
    except ValueError as exc:
        if 'Private' in str(exc): raise
    return url

def profile_value(label: str, user):
    key = label.lower().strip()
    name = (user.name or '').strip()
    if any(x in key for x in ['first name','firstname','fname']): return name.split(' ')[0] if name else None
    if any(x in key for x in ['last name','lastname','lname']): return ' '.join(name.split(' ')[1:]) or None
    if key in ['name','full name','fullname','your name']: return name or None
    if 'email' in key: return user.email
    if any(x in key for x in ['phone','mobile','telephone']): return user.phone
    if 'linkedin' in key: return user.linkedin_link
    if 'github' in key: return user.github_link
    if 'portfolio' in key or 'website' in key: return next(iter(user.portfolio_links), None)
    if 'location' in key or key == 'city': return user.location
    if 'notice' in key: return user.notice_period
    if 'salary' in key: return user.expected_salary
    return None

def readiness(user, resume, job):
    issues=[]
    if not user.name: issues.append('Add your full name in Profile')
    if not user.email: issues.append('Add an email address')
    if not resume: issues.append('Upload and select an active resume')
    try: validate_apply_url(job.apply_url or job.url)
    except ValueError as exc: issues.append(str(exc))
    return {'ready':not issues,'issues':issues,'mode':'DRY_RUN','note':'A dry run never submits. Live completion requires confirmation from the destination site.'}
