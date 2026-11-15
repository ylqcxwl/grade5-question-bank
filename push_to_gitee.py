#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""一键在 Gitee 创建仓库并推送本地题库。

用法：
    export GITEE_TOKEN=你的私人令牌
    python push_to_gitee.py                 # 默认私有仓库
    python push_to_gitee.py --public       # 公开仓库
    python push_to_gitee.py --name my-repo # 自定义仓库名

令牌也可放在同目录的 .gitee_token 文件里（已被 .gitignore 忽略，不会上传）。
令牌申请：https://gitee.com/profile/personal_access_tokens  勾选 projects 权限。
"""
from __future__ import unicode_literals

import argparse
import io
import json
import os
import ssl
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://gitee.com/api/v5"
ROOT = os.path.dirname(os.path.abspath(__file__))

DEFAULT_NAME = "grade5-question-bank"
DEFAULT_DESC = ("人教版 2026 秋新教材 五年级上册 语文/数学/英语 4000 题题库，"
                "含总集、三科分册与可重跑的生成脚本，格式为「题了个题」question-format")


def log(msg):
    print(msg)
    sys.stdout.flush()


def get_token():
    t = os.environ.get("GITEE_TOKEN", "").strip()
    if not t:
        p = os.path.join(ROOT, ".gitee_token")
        if os.path.isfile(p):
            t = io.open(p, encoding="utf-8").read().strip()
    return t


def api(method, path, token=None, data=None):
    url = BASE + path
    if token:
        url += ("&" if "?" in url else "?") + "access_token=" + urllib.parse.quote(token, safe="")
    body = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None
    req = urllib.request.Request(
        url, data=body, method=method,
        headers={"Content-Type": "application/json", "User-Agent": "WorkBuddy/1.0"},
    )
    # 本机证书吊销检查离线（curl 需 -k），此处同样放宽校验
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
            raw = r.read().decode("utf-8", "replace")
            return r.status, (json.loads(raw) if raw.strip() else {})
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except ValueError:
            payload = {"raw": raw[:400]}
        return e.code, payload
    except Exception as e:                       # noqa: BLE001
        return 0, {"error": str(e)}


def git(*args):
    p = subprocess.run(
        ["git"] + list(args), cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    out = p.stdout.decode("utf-8", "replace").strip()
    if out:
        log("    " + out.replace("\n", "\n    "))
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", default=DEFAULT_NAME, help="仓库名")
    ap.add_argument("--public", action="store_true", help="公开仓库（默认私有）")
    ap.add_argument("--desc", default=DEFAULT_DESC, help="仓库描述")
    ap.add_argument("--owner", default="", help="Gitee 用户名；无法自动推断时手动指定")
    a = ap.parse_args()

    token = get_token()
    if not token:
        log("✗ 未找到 Gitee 私人令牌。请设置环境变量 GITEE_TOKEN，或写入同目录 .gitee_token 文件。")
        return 2

    log("[1/5] 校验令牌并获取账号 …")
    owner = a.owner.strip()
    if not owner:
        code, me = api("GET", "/user", token=token)
        if code == 200 and me.get("login"):
            owner = me["login"]
            log("    账号：%s（%s）" % (owner, me.get("name") or "-"))
        else:
            # 只勾 projects 权限的令牌可能读不了 /user，改从仓库列表推断
            log("    ! /user 不可用（HTTP %s），改从仓库列表推断账号 …" % code)
            code2, repos = api("GET", "/user/repos?per_page=1", token=token)
            if code2 == 200 and isinstance(repos, list) and repos:
                owner = (repos[0].get("full_name") or "/").split("/")[0]
                log("    账号：%s（由仓库列表推断）" % owner)
    if not owner:
        log("✗ 令牌无效，或无法自动获取用户名。请用 --owner 你的用户名 指定，或给令牌补上 user_info 权限。")
        return 3

    repo = a.name
    private = not a.public
    log("[2/5] 检查远程仓库 %s/%s …" % (owner, repo))
    code, info = api("GET", "/repos/%s/%s" % (owner, repo), token=token)
    if code == 200:
        log("    已存在，直接复用：%s" % info.get("html_url"))
    else:
        log("    不存在，创建中（%s）…" % ("公开" if not private else "私有"))
        code, info = api("POST", "/user/repos", token=token, data={
            "name": repo,
            "description": a.desc,
            "private": private,
            "auto_init": False,
            "has_issues": True,
            "has_wiki": False,
        })
        if code not in (200, 201):
            log("✗ 创建失败：HTTP %s %s" % (code, info.get("message") or info.get("error") or info))
            return 4
        log("    创建成功：%s" % info.get("html_url"))

    clean_url = "https://gitee.com/%s/%s.git" % (owner, repo)
    log("[3/5] 设置 remote origin（不含令牌）…")
    git("remote", "remove", "origin")
    if git("remote", "add", "origin", clean_url) != 0:
        log("✗ remote 设置失败")
        return 5

    log("[4/5] 推送 master …")
    auth_url = "https://%s:%s@%s/%s/%s.git" % (
        urllib.parse.quote(owner, safe=""),
        urllib.parse.quote(token, safe=""),
        "gitee.com", owner, repo,
    )
    rc = subprocess.run(
        ["git", "push", "-u", auth_url, "HEAD:refs/heads/master"],
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    out = rc.stdout.decode("utf-8", "replace").strip()
    # 输出中可能回显带令牌的 URL，做一次脱敏
    log("    " + out.replace(auth_url, clean_url).replace("\n", "\n    "))
    if rc.returncode != 0:
        log("✗ 推送失败（exit %d）" % rc.returncode)
        return 6

    log("[5/5] 核对远端内容 …")
    code, tree = api("GET", "/repos/%s/%s/contents/questions" % (owner, repo), token=token)
    if code == 200 and isinstance(tree, list):
        log("    questions/ 下 %d 个文件：" % len(tree))
        for f in tree:
            log("      - %s (%s bytes)" % (f.get("name"), f.get("size")))
    else:
        log("    ! 目录核对未通过：HTTP %s %s" % (code, tree.get("message") if isinstance(tree, dict) else tree))

    log("")
    log("✓ 完成：https://gitee.com/%s/%s" % (owner, repo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
