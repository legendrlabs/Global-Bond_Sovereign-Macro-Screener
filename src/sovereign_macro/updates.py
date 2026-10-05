"""Stable GitHub wheel updates. Installation is called only after approval."""
from dataclasses import dataclass
from email.parser import Parser
import hashlib
from importlib.metadata import distribution, PackageNotFoundError
from io import BytesIO
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import zipfile
import requests
from . import __version__

REPOSITORY='legendrlabs/Global-Bond_Sovereign-Macro-Screener'
LATEST_URL=f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
MAX_WHEEL_BYTES=20*1024*1024

class UpdateError(Exception):
    pass

@dataclass(frozen=True)
class Release:
    version: str
    name: str
    url: str
    sha256: str
    size: int

def version_tuple(value):
    if not isinstance(value,str) or not re.fullmatch(r'(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)',value):
        raise UpdateError('지원하지 않는 버전 형식입니다.')
    return tuple(map(int,value.split('.')))

def parse_release(data,current=__version__):
    if not isinstance(data,dict): raise UpdateError('릴리스 응답을 확인할 수 없습니다.')
    if data.get('draft') is True or data.get('prerelease') is True: return None
    if data.get('draft') is not False or data.get('prerelease') is not False:
        raise UpdateError('정식 릴리스 여부를 확인할 수 없습니다.')
    tag=data.get('tag_name','')
    if not isinstance(tag,str) or not tag.startswith('v'): raise UpdateError('릴리스 태그가 잘못되었습니다.')
    version=tag[1:]
    if version_tuple(version)<=version_tuple(current): return None
    name=f'sovereign_macro_screener-{version}-py3-none-any.whl'
    assets=data.get('assets')
    if not isinstance(assets,list): raise UpdateError('설치 파일 목록이 없습니다.')
    matching=[a for a in assets if isinstance(a,dict) and a.get('name')==name]
    if len(matching)!=1: raise UpdateError('이 버전의 설치 파일을 확인할 수 없습니다.')
    asset=matching[0];url=f'https://github.com/{REPOSITORY}/releases/download/{tag}/{name}'
    digest=asset.get('digest','');size=asset.get('size')
    if asset.get('browser_download_url')!=url or not isinstance(digest,str) or not re.fullmatch(r'sha256:[0-9a-f]{64}',digest):
        raise UpdateError('설치 파일의 출처 또는 SHA-256을 확인할 수 없습니다.')
    if not isinstance(size,int) or isinstance(size,bool) or not 0<size<=MAX_WHEEL_BYTES:
        raise UpdateError('설치 파일 크기가 허용 범위를 벗어났습니다.')
    return Release(version,name,url,digest[7:],size)

def latest_release():
    try:
        response=requests.get(LATEST_URL,headers={'Accept':'application/vnd.github+json','User-Agent':'SovereignMacroScreener/'+__version__},timeout=(5,10))
        if response.status_code==404: return None
        response.raise_for_status()
        return parse_release(response.json())
    except (requests.RequestException,ValueError) as exc:
        raise UpdateError('새 버전을 확인하지 못했습니다. 현재 버전을 계속 사용합니다.') from exc

def download_wheel(release):
    try:
        with requests.get(release.url,stream=True,timeout=(5,20)) as response:
            response.raise_for_status();chunks=[];size=0
            for chunk in response.iter_content(65536):
                size+=len(chunk)
                if size>release.size or size>MAX_WHEEL_BYTES: raise UpdateError('다운로드 크기가 다릅니다.')
                chunks.append(chunk)
            return b''.join(chunks)
    except requests.RequestException as exc:
        raise UpdateError('설치 파일 다운로드에 실패했습니다.') from exc

def editable_install():
    try:
        text=distribution('sovereign-macro-screener').read_text('direct_url.json')
        return bool(text and json.loads(text).get('dir_info',{}).get('editable'))
    except (PackageNotFoundError,ValueError): return False

def install_release(release):
    if editable_install(): raise UpdateError('개발용 editable 설치입니다. 소스 작업을 보호하기 위해 자동 설치하지 않습니다. 배포용 가상환경에 일반 설치해 주세요.')
    body=download_wheel(release)
    if len(body)!=release.size or hashlib.sha256(body).hexdigest()!=release.sha256:
        raise UpdateError('설치 파일 무결성 검사가 실패했습니다. 설치하지 않았습니다.')
    try:
        with zipfile.ZipFile(BytesIO(body)) as archive:
            metadata=[n for n in archive.namelist() if n.endswith('.dist-info/METADATA')]
            if len(metadata)!=1 or archive.getinfo(metadata[0]).file_size>100000:
                raise UpdateError('설치 파일 메타데이터가 잘못되었습니다.')
            fields=Parser().parsestr(archive.read(metadata[0]).decode('utf-8'))
            if fields.get('Name')!='sovereign-macro-screener' or fields.get('Version')!=release.version:
                raise UpdateError('설치 파일의 프로그램 또는 버전이 다릅니다.')
    except (zipfile.BadZipFile,UnicodeError) as exc:
        raise UpdateError('설치 파일을 읽을 수 없습니다.') from exc
    with tempfile.TemporaryDirectory(prefix='sovereign-update-') as tmp:
        path=Path(tmp)/release.name;path.write_bytes(body)
        try:
            subprocess.run([sys.executable,'-m','pip','install','--upgrade',str(path)],check=True,timeout=180)
        except (subprocess.SubprocessError,OSError) as exc:
            raise UpdateError('프로그램 설치가 완료되지 않았습니다. 환경을 확인하고 다시 실행해 주세요.') from exc
