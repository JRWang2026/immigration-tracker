#!/usr/bin/env python3
"""解析SEEK邮件HTML，提取岗位信息"""
import re
import json
import os

# 读取三封新邮件的文本内容
files = [
    ("ICT_2147", r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\f219b38f-e9df-41b9-8fe7-c9aca9d46546\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782453431456-5e5c63.txt"),
    ("ICT_2025", r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\f219b38f-e9df-41b9-8fe7-c9aca9d46546\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782453431519-dc6df4.txt"),
    ("Admin_2358", r"C:\Users\Mr_Wang\.workbuddy\projects\c-Users-Mr_Wang-WorkBuddy-2026-06-20-14-48-36\f219b38f-e9df-41b9-8fe7-c9aca9d46546\tool-results\mcp-connector-proxy-qq-mail_GetMessage-1782453431373-daea12.txt"),
]

all_jobs = []

for label, filepath in files:
    print(f"\n{'='*80}")
    print(f"FILE: {label}")
    print(f"{'='*80}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Try to parse JSON first (GetMessage returns JSON)
    try:
        data = json.loads(content)
        if 'data' in data and 'data' in data['data']:
            html_body = data['data']['data'].get('body', '')
        elif 'data' in data:
            html_body = data['data'].get('body', content)
        else:
            html_body = content
    except:
        html_body = content
    
    # Decode HTML entities
    html_body = html_body.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    
    # Find all job cards - SEEK emails have specific patterns
    # Pattern 1: Job title in <a> tags with tracking links
    # Look for patterns like: job title, company, location, salary
    
    # Extract all text between relevant tags
    # Remove CSS/style sections first
    cleaned = re.sub(r'<style[^>]*>.*?</style>', '', html_body, flags=re.DOTALL)
    
    # Find all SEEK job links
    seek_links = re.findall(r'https?://www\.seek\.co\.nz/job/[^\s"<>]+', cleaned)
    
    # Find job title - company patterns
    # In SEEK emails, jobs are typically in table rows
    # Let's extract all text content
    text_content = re.sub(r'<[^>]+>', '\n', cleaned)
    text_content = re.sub(r'\n{3,}', '\n\n', text_content)
    text_content = re.sub(r'[ \t]+', ' ', text_content)
    
    # Print first 3000 chars to understand structure
    print("\n--- TEXT PREVIEW (first 5000 chars) ---")
    print(text_content[:5000])
    
    # Look for job entry patterns - typically "JobTitle  CompanyName  Location  Salary"
    # Find lines with salary patterns like $XX,XXX – $XX,XXX
    salary_pattern = re.compile(r'\$[\d,]+(?:\s*[–-]\s*\$[\d,]+)?(?:\s*(?:per|a)\s*(?:year|annum|month|hour))?', re.IGNORECASE)
    
    lines = text_content.split('\n')
    for i, line in enumerate(lines[:200]):
        stripped = line.strip()
        if stripped:
            print(f"  L{i}: {stripped[:200]}")

print(f"\n\nFound {len(seek_links)} SEEK links total across all emails")
