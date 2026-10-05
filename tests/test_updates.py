"""Approval, release integrity, and report freshness boundaries."""
import hashlib
import io
import json
import tempfile
import shutil
import unittest
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path
from unittest.mock import patch
import importlib

REPO='legendrlabs/Global-Bond_Sovereign-Macro-Screener'
NAME='sovereign_macro_screener-0.2.0-py3-none-any.whl'
URL=f'https://github.com/{REPO}/releases/download/v0.2.0/{NAME}'

def wheel():
    b=io.BytesIO()
    with zipfile.ZipFile(b,'w') as z:
        z.writestr('sovereign_macro_screener-0.2.0.dist-info/METADATA','Metadata-Version: 2.1\nName: sovereign-macro-screener\nVersion: 0.2.0\n')
    return b.getvalue()

def release(body=None):
    body=wheel() if body is None else body
    return dict(tag_name='v0.2.0',draft=False,prerelease=False,assets=[dict(name=NAME,browser_download_url=URL,size=len(body),digest='sha256:'+hashlib.sha256(body).hexdigest())])

class UpdateTests(unittest.TestCase):
    def mod(self):
        spec=importlib.util.find_spec('sovereign_macro.updates')
        self.assertIsNotNone(spec,'updates module missing')
        return importlib.import_module('sovereign_macro.updates')

    def test_select_new_stable_wheel_with_exact_repo_and_hash(self):
        m=self.mod();r=m.parse_release(release(),'0.1.0')
        self.assertEqual((r.version,r.url,r.name),('0.2.0',URL,NAME))
        self.assertIsNone(m.parse_release(release(),'0.2.0'))
        self.assertIsNone(m.parse_release(release(),'1.0.0'))

    def test_reject_untrusted_missing_digest_wrong_version_or_ambiguous_assets(self):
        m=self.mod()
        for change in ('host','digest','name','size','duplicate'):
            data=release();a=data['assets'][0]
            if change=='host':a['browser_download_url']=URL.replace('github.com','evil.example')
            if change=='digest':a.pop('digest')
            if change=='name':a['name']=NAME.replace('0.2.0','0.3.0')
            if change=='size':a['size']=999999999
            if change=='duplicate':data['assets'].append(dict(a))
            with self.subTest(change=change), self.assertRaises(m.UpdateError):m.parse_release(data,'0.1.0')
        for field in ('draft','prerelease'):
            data=release();data[field]=True
            self.assertIsNone(m.parse_release(data,'0.1.0'))

    def test_install_hash_mismatch_never_invokes_pip(self):
        m=self.mod();r=m.parse_release(release(),'0.1.0')
        with patch.object(m,'download_wheel',return_value=b'tampered'),patch.object(m,'editable_install',return_value=False),patch.object(m.subprocess,'run') as pip:
            with self.assertRaises(m.UpdateError):m.install_release(r)
            pip.assert_not_called()

    def test_install_verified_wheel_uses_current_python_without_shell(self):
        m=self.mod();r=m.parse_release(release(),'0.1.0')
        with patch.object(m,'download_wheel',return_value=wheel()),patch.object(m,'editable_install',return_value=False),patch.object(m.subprocess,'run') as pip:
            m.install_release(r)
            argv=pip.call_args.args[0]
            self.assertEqual(argv[:4],[m.sys.executable,'-m','pip','install'])
            self.assertTrue(argv[-1].endswith(NAME))
            self.assertNotIn('shell',pip.call_args.kwargs)

class InteractiveTests(unittest.TestCase):
    def mod(self):
        spec=importlib.util.find_spec('sovereign_macro.interactive')
        self.assertIsNotNone(spec,'interactive module missing')
        return importlib.import_module('sovereign_macro.interactive')

    def report(self,root,mode=False):
        dest=Path(root)/'runs'/'fixture';dest.mkdir(parents=True)
        (dest/'index.html').write_text('<html>old report</html>')
        (dest/'quality.json').write_text(json.dumps(dict(public_output=mode,demo=False,status='DATA_HOLD',baseline_usable=6)))
        (Path(root)/'current.json').write_text(json.dumps(dict(path='runs/fixture',as_of='2026-10-04',generated_at='2026-10-04T02:00:00+00:00')))
        return dest

    def test_fresh_partial_report_is_openable_but_old_or_wrong_mode_requires_refresh(self):
        m=self.mod();now=datetime(2026,10,4,3,tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as root:
            dest=self.report(root)
            state=m.data_state(root,date(2026,10,4),False,now)
            self.assertFalse(state.due);self.assertEqual(state.report,dest/'index.html')
            self.assertTrue(m.data_state(root,date(2026,10,5),False,now).due)
            self.assertIsNone(m.data_state(root,date(2026,10,4),True,now).report)

    def test_pointer_escape_or_missing_quality_cannot_open_report(self):
        m=self.mod();now=datetime(2026,10,4,3,tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as root:
            dest=self.report(root);(dest/'quality.json').unlink()
            self.assertIsNone(m.data_state(root,date(2026,10,4),False,now).report)
            (Path(root)/'current.json').write_text(json.dumps(dict(path='../../secret',as_of='2026-10-04',generated_at=now.isoformat())))
            self.assertIsNone(m.data_state(root,date(2026,10,4),False,now).report)

    def test_confirmation_defaults_to_no_eof_and_noninteractive(self):
        m=self.mod()
        self.assertFalse(m.confirm('설치?',interactive=False,input_fn=lambda _:self.fail('must not read input')))
        self.assertFalse(m.confirm('설치?',interactive=True,input_fn=lambda _:''))
        self.assertTrue(m.confirm('설치?',interactive=True,input_fn=lambda _:'y'))
        def eof(_):raise EOFError()
        self.assertFalse(m.confirm('설치?',interactive=True,input_fn=eof))

    def test_declining_both_keeps_old_report_and_does_not_install_or_collect(self):
        m=self.mod()
        with tempfile.TemporaryDirectory() as root:
            old=self.report(root)
            with patch.object(m.updates,'latest_release',return_value=m.updates.parse_release(release(),'0.1.0')),patch.object(m.updates,'install_release') as install:
                status=m.run_app(root,date(2026,10,5),False,lambda:self.fail('must not collect'),interactive=True,input_fn=lambda _:'n',open_browser=False)
            self.assertEqual(status,0);install.assert_not_called()
            self.assertIn('fixture',(Path(root)/'current.json').read_text())
            self.assertEqual((old/'index.html').read_text(),'<html>old report</html>')

    def test_update_failure_continues_to_data_prompt_and_approved_refresh(self):
        m=self.mod();called=[]
        with tempfile.TemporaryDirectory() as root:
            dest=Path(root)/'new';dest.mkdir();(dest/'index.html').write_text('new')
            with patch.object(m.updates,'latest_release',side_effect=m.updates.UpdateError('offline')):
                status=m.run_app(root,date(2026,10,4),False,lambda:(called.append('collect') or dest,0),interactive=True,input_fn=lambda _:'y',open_browser=False)
            self.assertEqual(status,0);self.assertEqual(called,['collect'])

    def test_approved_program_update_exits_for_restart_without_collecting(self):
        m=self.mod()
        with tempfile.TemporaryDirectory() as root:
            with patch.object(m.updates,'latest_release',return_value=m.updates.parse_release(release(),'0.1.0')),patch.object(m.updates,'install_release') as install:
                status=m.run_app(root,date(2026,10,4),False,lambda:self.fail('must restart first'),interactive=True,input_fn=lambda _:'y',open_browser=False)
            self.assertEqual(status,0);install.assert_called_once()

    def test_noninteractive_never_checks_installs_or_collects(self):
        m=self.mod()
        with tempfile.TemporaryDirectory() as root,patch.object(m.updates,'latest_release') as check:
            status=m.run_app(root,date(2026,10,4),False,lambda:self.fail('must not collect'),interactive=False,open_browser=False)
            self.assertEqual(status,0);check.assert_not_called()

class ReleaseWorkflowTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('git') and shutil.which('bash'),'release gate runs on GitHub Linux')
    def test_release_gate_accepts_matching_stable_tag_and_blocks_mismatch_or_nonmain(self):
        import os
        import subprocess
        import yaml
        workflow=Path(__file__).resolve().parents[1]/'.github/workflows/release.yml'
        data=yaml.safe_load(workflow.read_text())
        step=next(s for s in data['jobs']['build']['steps'] if s.get('name')=='Require a main commit and matching stable version')
        with tempfile.TemporaryDirectory() as root:
            dest=Path(root);(dest/'src/sovereign_macro').mkdir(parents=True)
            (dest/'src/sovereign_macro/__init__.py').write_text('__version__="0.1.0"\n')
            (dest/'pyproject.toml').write_text('[project]\nversion="0.1.0"\n')
            def git(*args):return subprocess.run(['git',*args],cwd=root,check=True,capture_output=True)
            git('init');git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','--allow-empty','-m','base')
            git('update-ref','refs/remotes/origin/main','HEAD')
            env={**os.environ,'GITHUB_REF_NAME':'v0.1.0'}
            valid=subprocess.run(['bash','-e','-c',step['run']],cwd=root,env=env,capture_output=True,text=True)
            self.assertEqual(valid.returncode,0,valid.stderr)
            main_env={**env,'GITHUB_REF_NAME':'main','GITHUB_REF_TYPE':'branch'}
            main_run=subprocess.run(['bash','-e','-c',step['run']],cwd=root,env=main_env,capture_output=True,text=True)
            self.assertEqual(main_run.returncode,0,main_run.stderr)
            main_env['GITHUB_REF_NAME']='release/stable-0.1.1'
            nonmain=subprocess.run(['bash','-e','-c',step['run']],cwd=root,env=main_env,capture_output=True)
            self.assertNotEqual(nonmain.returncode,0)
            env['GITHUB_REF_NAME']='v0.2.0'
            wrong=subprocess.run(['bash','-e','-c',step['run']],cwd=root,env=env,capture_output=True)
            self.assertNotEqual(wrong.returncode,0)
            env['GITHUB_REF_NAME']='v0.1.0'
            git('-c','user.name=Test','-c','user.email=test@example.invalid','commit','--allow-empty','-m','unmerged')
            unmerged=subprocess.run(['bash','-e','-c',step['run']],cwd=root,env=env,capture_output=True)
            self.assertNotEqual(unmerged.returncode,0)
