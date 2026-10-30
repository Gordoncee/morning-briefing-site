"""External-clock checks do not need a live credential or modify GitHub."""
import datetime as dt
import base64
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("news_clock", Path(__file__).resolve().parents[1] / "ops/check_daily_news.py")
clock = importlib.util.module_from_spec(spec)
spec.loader.exec_module(clock)
TODAY = "2026-10-30"
NOW = dt.datetime(2026, 10, 30, 0, 5, tzinfo=dt.timezone.utc)
VERSION = "f" * 64
EXPECTED = {"schema_version": 1, "latest": TODAY, "archive_sha256": VERSION}
HTML = ('<meta name="news-latest-date" content="' + TODAY + '">'
        '<meta name="news-archive-version" content="' + VERSION + '">'
        '<a data-news-date="' + TODAY + '">today</a>')


class TriggerTests(unittest.TestCase):
    def test_current_site_exits_without_credential_or_github_dispatch(self):
        def fetch(url, **kwargs):
            return json.dumps(EXPECTED) if url == clock.ORIGIN else HTML
        with tempfile.TemporaryDirectory() as temporary:
            result = clock.check(Path(temporary), Path("/missing/token"), fetch=fetch, now=NOW)
        self.assertEqual(result["reason"], "current")
        self.assertFalse(result["dispatched"])

    def test_source_missing_today_and_stale_public_site_are_distinct(self):
        self.assertEqual(clock.freshness(dict(EXPECTED, latest="2026-10-29"), HTML, TODAY), "today-missing-at-origin")
        self.assertEqual(clock.freshness(EXPECTED, HTML.replace(TODAY, "2026-10-29"), TODAY), "today-missing-on-website")
        self.assertEqual(clock.freshness(EXPECTED, HTML.replace(VERSION, "0"*64), TODAY), "website-version-mismatch")

    def test_dry_run_never_reads_secret_or_mutates(self):
        def fetch(url, **kwargs):
            self.assertFalse(kwargs)
            return json.dumps(dict(EXPECTED, latest="2026-10-29")) if url == clock.ORIGIN else HTML
        with tempfile.TemporaryDirectory() as temporary:
            result = clock.check(Path(temporary), Path("/missing/token"), True, fetch, NOW)
            self.assertEqual(list(Path(temporary).iterdir()), [])
        self.assertFalse(result["dispatched"])

    def test_delayed_schedule_dispatches_once_then_cooldown_without_model_access(self):
        calls = []
        def fetch(url, **kwargs):
            calls.append((url, kwargs))
            if url == clock.ORIGIN:return json.dumps(dict(EXPECTED, latest="2026-10-29"))
            if url == clock.PUBLIC:return HTML
            if "runs?" in url:return '{"workflow_runs":[]}'
            self.assertEqual(kwargs["payload"], {"ref":"main","inputs":{"date":TODAY,"force":"false"}})
            return ""
        with tempfile.TemporaryDirectory() as temporary, patch.object(clock, "read_token", return_value="github_pat_TEST"):
            state = Path(temporary)
            first = clock.check(state, Path("unused"), fetch=fetch, now=NOW)
            second = clock.check(state, Path("unused"), fetch=fetch, now=NOW)
            self.assertNotIn("github_pat_TEST", (state / "last-dispatch.json").read_text())
        self.assertTrue(first["dispatched"])
        self.assertEqual(second["action"], "dispatch-cooldown")
        self.assertEqual(sum(url.endswith("/dispatches") for url, _ in calls), 1)

    def test_active_github_run_avoids_duplicate_dispatch(self):
        def fetch(url, **kwargs):
            if url == clock.ORIGIN:return json.dumps(dict(EXPECTED, latest="2026-10-29"))
            if url == clock.PUBLIC:return HTML
            return json.dumps({"workflow_runs":[{"id":12,"status":"in_progress","created_at":"2026-10-30T00:00:00Z"}]})
        with tempfile.TemporaryDirectory() as temporary:
            result=clock.check(Path(temporary), Path("/missing/token"), fetch=fetch, now=NOW)
        self.assertEqual(result["action"], "wait-for-active-run")

    def test_beijing_date_at_utc_day_boundary(self):
        self.assertEqual(clock.freshness(EXPECTED, HTML, TODAY), "current")
        now=dt.datetime(2026,10,29,23,59,tzinfo=dt.timezone.utc)
        def fetch(url, **kwargs):return json.dumps(EXPECTED) if url==clock.ORIGIN else HTML
        result=clock.check(Path("unused"), Path("unused"), fetch=fetch, now=now)
        self.assertEqual(result["date"], TODAY)

    def test_broad_personal_oauth_tokens_and_insecure_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            token=Path(temporary)/"token"
            token.write_text("gho_DO_NOT_COPY_LOCAL_LOGIN")
            token.chmod(0o600)
            with self.assertRaises(ValueError):clock.read_token(token)
            token.write_text("github_pat_SCOPED_TEST")
            token.chmod(0o644)
            with self.assertRaises(ValueError):clock.read_token(token)
            token.chmod(0o600)
            self.assertEqual(clock.read_token(token), "github_pat_SCOPED_TEST")

    def test_app_token_is_scoped_to_news_actions_and_jwt_has_short_lifetime(self):
        from subprocess import CompletedProcess
        calls = []
        def fetch(url, **kwargs):
            calls.append((url, kwargs))
            self.assertEqual(kwargs["payload"], {"repositories":["morning-briefing-site"],
                                                 "permissions":{"actions":"write"}})
            return json.dumps({"token":"ghs_TEST", "permissions":{"actions":"write","metadata":"read"}})
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);key=root/"app.pem";key.write_text("TEST KEY");key.chmod(0o600)
            config=root/"app.json";config.write_text(json.dumps({"repository":clock.REPOSITORY,
                "client_id":"IvTEST","installation_id":123,"private_key_file":str(key)}))
            with patch.object(clock.subprocess,"run",return_value=CompletedProcess([],0,b"signature")):
                self.assertEqual(clock.app_installation_token(config,fetch,NOW),"ghs_TEST")
            jwt=calls[0][1]["token"]
            payload=json.loads(base64.urlsafe_b64decode(jwt.split(".")[1]+"=="))
            self.assertEqual(payload["iat"],int(NOW.timestamp())-60)
            self.assertEqual(payload["exp"],int(NOW.timestamp())+540)
            self.assertNotIn("TEST KEY",jwt)

    def test_server_timer_has_bounded_resources_and_reboot_persistence(self):
        directory=Path(__file__).resolve().parents[1]/"ops"
        service=(directory/"fazhi-news-trigger.service").read_text()
        timer=(directory/"fazhi-news-trigger.timer").read_text()
        for setting in ["Type=oneshot","MemoryMax=48M","CPUQuota=10%","User=fazhi-news-trigger"]:
            self.assertIn(setting,service)
        self.assertIn("Persistent=true",timer)
        self.assertEqual(timer.count("OnCalendar="),7)
        self.assertIn("13:15:00 Asia/Shanghai",timer)
        self.assertIn("16:15:00 Asia/Shanghai",timer)

    def test_credentials_cannot_be_sent_to_an_arbitrary_url(self):
        with self.assertRaises(ValueError):
            clock.request("https://example.org/actions/workflows/test",token="SECRET")

    def test_stale_running_job_does_not_block_all_later_attempts(self):
        self.assertIsNone(clock.active_run({"workflow_runs":[
            {"id":1,"status":"in_progress","created_at":"2026-10-29T23:00:00Z"}]},NOW))

    def test_real_openssl_signature_verifies_without_any_network(self):
        import subprocess
        import shutil
        if not shutil.which("openssl"):self.skipTest("OpenSSL not installed")
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);key=root/"app.pem"
            subprocess.run(["openssl","genrsa","-out",str(key),"2048"],check=True,
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            key.chmod(0o600)
            config=root/"app.json";config.write_text(json.dumps({"repository":clock.REPOSITORY,
                "client_id":"IvTEST","installation_id":123,"private_key_file":str(key)}))
            captured=[]
            def fetch(url,**kwargs):
                captured.append(kwargs["token"])
                return '{"token":"ghs_TEST","permissions":{"actions":"write","metadata":"read"}}'
            clock.app_installation_token(config,fetch,NOW)
            jwt=captured[0];head,payload,signature=jwt.split(".")
            (root/"message").write_bytes((head+"."+payload).encode())
            (root/"signature").write_bytes(base64.urlsafe_b64decode(signature+"=="))
            with (root/"public.pem").open("wb") as output:
                subprocess.run(["openssl","rsa","-in",str(key),"-pubout"],stdout=output,
                               stderr=subprocess.DEVNULL,check=True)
            result=subprocess.run(["openssl","dgst","-sha256","-verify",str(root/"public.pem"),
                "-signature",str(root/"signature"),str(root/"message")],capture_output=True,check=True)
            self.assertIn(b"Verified OK",result.stdout)


if __name__ == "__main__":unittest.main()
