#!/usr/bin/env python3
"""Local, one-use GitHub App registration helper. Never prints credentials.

The owner confirms creation/installation in GitHub's browser UI. A loopback-only
callback exchanges the approved manifest code and saves only the App key/IDs in
a private temporary directory, ready for an encrypted SSH transfer.
"""
import argparse
from html import escape
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
from pathlib import Path
import re
import secrets
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def private_write(path, value):
    fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as stream:
        stream.write(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", required=True, type=Path)
    args = parser.parse_args()
    args.directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    args.directory.chmod(0o700)
    nonce = secrets.token_urlsafe(24)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Callback query strings contain temporary credentials.

        def send_page(self, body, status=200):
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Content-Security-Policy", "default-src 'none'; form-action https://github.com; base-uri 'none'")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def do_GET(self):
            parsed = urlsplit(self.path)
            query = parse_qs(parsed.query)
            if parsed.path == "/" + nonce + "/":
                manifest = {
                    "name":"Fazhi News Clock 20261030", "url":"https://fazhi.cc/news/",
                    "description":"Triggers daily news GitHub Actions from an independent clock. Only morning-briefing-site; no contents or secrets permissions.",
                    "redirect_url": base + "/" + nonce + "/created",
                    "setup_url": base + "/" + nonce + "/installed",
                    "public":False, "default_permissions":{"actions":"write"},
                    "default_events":[], "hook_attributes":{"url":"https://fazhi.cc/news/","active":False},
                    "request_oauth_on_install":False,
                }
                self.send_page('<!doctype html><meta charset="utf-8"><title>每日资讯独立触发授权</title>'
                    '<h1>每日资讯独立触发授权</h1><p>账号：Gordoncee。仅安装到 morning-briefing-site 仓库。</p>'
                    '<p>权限：GitHub Actions 读写，用于查看和启动每日资讯任务。不授予仓库内容写入、Secrets 管理或个人账号权限。</p>'
                    '<p>专用应用密钥经 SSH 保存到 47.117.77.217，不复制本机 GitHub 登录凭证。运行令牌自动短期签发。</p>'
                    '<form action="https://github.com/settings/apps/new?state=' + nonce + '" method="post">'
                    '<input type="hidden" name="manifest" value="' + escape(json.dumps(manifest), quote=True) + '">'
                    '<button type="submit">前往 GitHub 核对应用授权</button></form>')
                return
            if parsed.path == "/" + nonce + "/created":
                code = query.get("code", [""])[0]
                if query.get("state") != [nonce] or not re.fullmatch(r"[A-Za-z0-9_-]{20,200}", code):
                    self.send_page("Invalid registration state.", 400);return
                try:
                    req = Request("https://api.github.com/app-manifests/" + code + "/conversions",
                                  data=b"", headers={"Accept":"application/vnd.github+json",
                                  "X-GitHub-Api-Version":"2026-03-10","User-Agent":"fazhi-news-app-registration"})
                    with build_opener(NoRedirect()).open(req,timeout=25) as response:
                        app=json.loads(response.read(100000))
                    permissions=app.get("permissions",{})
                    if app.get("owner",{}).get("login","").lower()!="gordoncee" or permissions.get("actions")!="write" or set(permissions)-{"actions","metadata"}:
                        raise ValueError("unexpected-owner-or-permissions")
                    private_write(args.directory/"app-key.pem",app["pem"])
                    metadata={k:app[k] for k in ["id","slug","client_id","html_url"]}
                    metadata.update(repository="Gordoncee/morning-briefing-site",permissions=permissions)
                    private_write(args.directory/"registration.json",json.dumps(metadata,indent=2)+"\n")
                    print(json.dumps({"stage":"app-created","app_id":app["id"],"slug":app["slug"]}),flush=True)
                    self.send_page('<h1>专用应用已建立</h1><p>密钥已安全保存，无需复制。</p><p><a href="https://github.com/apps/' + escape(app["slug"]) + '/installations/new">继续选择唯一的资讯仓库</a></p>')
                except Exception as error:
                    print(json.dumps({"stage":"registration-error","error":type(error).__name__}),flush=True)
                    self.send_page("Registration exchange failed. No credentials are shown.",500)
                return
            if parsed.path == "/" + nonce + "/installed":
                installation=query.get("installation_id",[""])[0]
                if not re.fullmatch(r"[0-9]+",installation):
                    self.send_page("Invalid installation.",400);return
                private_write(args.directory/"installation.json",json.dumps({"installation_id":int(installation)})+"\n")
                print(json.dumps({"stage":"app-installed","installation_id":int(installation)}),flush=True)
                self.send_page('<h1>独立触发权限已建立</h1><p>接下来通过 SSH 安装专用凭证并实测补跑。密钥不会显示在此页面。</p>')
                return
            self.send_page("Not found.",404)

    server=HTTPServer(("127.0.0.1",0),Handler)
    base="http://127.0.0.1:"+str(server.server_port)
    print(json.dumps({"registration_url":base+"/"+nonce+"/","private_directory":str(args.directory)}),flush=True)
    server.serve_forever()


if __name__=="__main__":main()
