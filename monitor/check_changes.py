#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import requests
from datetime import datetime

TARGET_REPO = "hhhhccccccc/Game"
GITHUB_API = "https://api.github.com"
WECHAT_WEBHOOK_URL = os.environ.get("WECHAT_WEBHOOK_URL")
LAST_COMMIT_FILE = "monitor/last_commit.txt"

def get_latest_commit():
    url = f"{GITHUB_API}/repos/{TARGET_REPO}/commits"
    try:
        response = requests.get(url, timeout=30, headers={"User-Agent": "Monitor"})
        if response.status_code == 200:
            commits = response.json()
            if commits:
                return commits[0]
        print(f"Error: HTTP {response.status_code}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_commit_details(commit_sha):
    url = f"{GITHUB_API}/repos/{TARGET_REPO}/commits/{commit_sha}"
    try:
        response = requests.get(url, timeout=30, headers={"User-Agent": "Monitor"})
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def read_last_commit():
    try:
        if os.path.exists(LAST_COMMIT_FILE):
            with open(LAST_COMMIT_FILE, 'r') as f:
                return f.read().strip()
    except:
        pass
    return None

def save_last_commit(commit_sha):
    try:
        os.makedirs(os.path.dirname(LAST_COMMIT_FILE), exist_ok=True)
        with open(LAST_COMMIT_FILE, 'w') as f:
            f.write(commit_sha)
    except Exception as e:
        print(f"Save error: {e}")

def generate_summary(commit, details):
    sha = commit['sha'][:8]
    message = commit['commit']['message'].split('\n')[0]
    author = commit['commit']['author']['name']
    date = commit['commit']['author']['date'][:10]
    
    total_additions = 0
    total_deletions = 0
    files_list = []
    
    if details and 'files' in details:
        stats = details.get('stats', {})
        total_additions = stats.get('additions', 0)
        total_deletions = stats.get('deletions', 0)
        
        for f in details['files'][:15]:
            status = f.get('status', 'modified')
            emoji = {'added': '🟢', 'modified': '🟡', 'removed': '🔴'}.get(status, '⚪')
            filename = f.get('filename', 'unknown')
            adds = f.get('additions', 0)
            dels = f.get('deletions', 0)
            files_list.append(f"{emoji} {filename} (+{adds}/-{dels})")
        
        if len(details['files']) > 15:
            files_list.append(f"... and {len(details['files']) - 15} more files")
    
    lines = [
        f"🎮 **Game Repo Update**",
        f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"",
        f"📊 **Overview**",
        f"   • Commit: `{sha}`",
        f"   • Author: {author}",
        f"   • Date: {date}",
        f"   • Changes: +{total_additions} / -{total_deletions}",
        f"",
        f"📝 **Message**",
        f"   {message}",
        f"",
    ]
    
    if files_list:
        lines.append("📁 **Files Changed**")
        for f in files_list:
            lines.append(f"   {f}")
        lines.append("")
    
    lines.append(f"🔗 **View**: https://github.com/{TARGET_REPO}/commit/{commit['sha']}")
    
    return "\n".join(lines)

def send_to_wechat(message):
    if not WECHAT_WEBHOOK_URL:
        print("No webhook URL")
        return False
    
    try:
        payload = {
            "msgtype": "markdown",
            "markdown": {"content": message}
        }
        response = requests.post(WECHAT_WEBHOOK_URL, json=payload, timeout=30)
        result = response.json()
        return result.get("errcode") == 0
    except Exception as e:
        print(f"Send error: {e}")
        return False

def main():
    print("Monitoring Game repo...")
    
    last_commit = read_last_commit()
    print(f"Last: {last_commit[:8] if last_commit else 'None'}")
    
    latest = get_latest_commit()
    if not latest:
        print("Failed to get latest commit")
        sys.exit(1)
    
    latest_sha = latest['sha']
    print(f"Latest: {latest_sha[:8]}")
    
    if last_commit == latest_sha:
        print("No new commits")
        return
    
    print("New commit found!")
    
    details = get_commit_details(latest_sha)
    summary = generate_summary(latest, details)
    
    if summary and send_to_wechat(summary):
        save_last_commit(latest_sha)
        print("Success!")
    else:
        print("Failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
