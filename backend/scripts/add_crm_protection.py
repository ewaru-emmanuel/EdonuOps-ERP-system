"""
Script to add @require_permission decorators to remaining CRM routes
This script will add protection to routes that don't have it yet
"""

import re

# Read the CRM routes file
with open('modules/crm/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Routes that need protection (route pattern -> permission)
routes_to_protect = {
    r'@crm_bp\.route\(\'/ai/score-lead\'': 'crm.leads.update',
    r'@crm_bp\.route\(\'/ai/next-actions\'': 'crm.leads.read',
    r'@crm_bp\.route\(\'/ai/extract-entities\'': 'crm.contacts.create',
    r'@crm_bp\.route\(\'/ai/suggest-mapping\'': 'crm.contacts.update',
    r'@crm_bp\.route\(\'/ai/generate-email\'': 'crm.communications.create',
    r'@crm_bp\.route\(\'/email/sync\'': 'crm.communications.read',
    r'@crm_bp\.route\(\'/deals/<int:opportunity_id>/win\'': 'crm.opportunities.update',
    r'@crm_bp\.route\(\'/activities\', methods=\[\'GET\'\]\)': 'crm.activities.read',
    r'@crm_bp\.route\(\'/activities\', methods=\[\'POST\'\]\)': 'crm.activities.create',
    r'@crm_bp\.route\(\'/time-entries\', methods=\[\'GET\'': 'crm.time_entries.read',
    r'@crm_bp\.route\(\'/time-entries\', methods=\[\'POST\'': 'crm.time_entries.create',
    r'@crm_bp\.route\(\'/time-entries/<int:entry_id>\'': 'crm.time_entries.update',
    r'@crm_bp\.route\(\'/reports/kpis\'': 'crm.reports.read',
    r'@crm_bp\.route\(\'/reports/forecast\'': 'crm.reports.read',
    r'@crm_bp\.route\(\'/reports/performance\'': 'crm.reports.read',
    r'@crm_bp\.route\(\'/reports/funnel\'': 'crm.reports.read',
    r'@crm_bp\.route\(\'/reports/stuck\'': 'crm.reports.read',
    r'@crm_bp\.route\(\'/pipelines\', methods=\[\'GET\'': 'crm.pipelines.read',
    r'@crm_bp\.route\(\'/pipelines\', methods=\[\'POST\'': 'crm.pipelines.create',
    r'@crm_bp\.route\(\'/pipelines/<int:pipeline_id>\'': 'crm.pipelines.update',
    r'@crm_bp\.route\(\'/tasks\', methods=\[\'GET\'': 'crm.tasks.read',
    r'@crm_bp\.route\(\'/tasks\', methods=\[\'POST\'': 'crm.tasks.create',
    r'@crm_bp\.route\(\'/tasks/<int:task_id>\'': 'crm.tasks.update',
    r'@crm_bp\.route\(\'/tasks/calendar\.ics\'': 'crm.tasks.read',
    r'@crm_bp\.route\(\'/marketing/sender\'': 'crm.marketing.read',
    r'@crm_bp\.route\(\'/marketing/segments\'': 'crm.marketing.read',
    r'@crm_bp\.route\(\'/marketing/templates\'': 'crm.marketing.read',
    r'@crm_bp\.route\(\'/marketing/campaigns\'': 'crm.marketing.read',
    r'@crm_bp\.route\(\'/marketing/sequences\'': 'crm.marketing.read',
    r'@crm_bp\.route\(\'/workflows\', methods=\[\'GET\'': 'crm.workflows.read',
    r'@crm_bp\.route\(\'/workflows\', methods=\[\'POST\'': 'crm.workflows.create',
    r'@crm_bp\.route\(\'/workflows/<int:wf_id>\'': 'crm.workflows.update',
    r'@crm_bp\.route\(\'/workflows/<int:wf_id>/toggle\'': 'crm.workflows.update',
    r'@crm_bp\.route\(\'/workflows/execution-history\'': 'crm.workflows.read',
    r'@crm_bp\.route\(\'/workflows/schedules\', methods=\[\'GET\'': 'crm.workflows.read',
    r'@crm_bp\.route\(\'/workflows/schedules\', methods=\[\'POST\'': 'crm.workflows.create',
    r'@crm_bp\.route\(\'/workflows/schedules/run\'': 'crm.workflows.update',
    r'@crm_bp\.route\(\'/kb/articles\', methods=\[\'GET\'': 'crm.knowledge_base.read',
    r'@crm_bp\.route\(\'/kb/articles\', methods=\[\'POST\'': 'crm.knowledge_base.create',
    r'@crm_bp\.route\(\'/kb/articles/<int:article_id>\'': 'crm.knowledge_base.update',
    # Public KB routes - no protection needed (they're public)
    r'@crm_bp\.route\(\'/kb/public\'': None,  # Public route
    r'@crm_bp\.route\(\'/kb/public/<int:article_id>\'': None,  # Public route
}

# Check which routes already have @require_permission
lines = content.split('\n')
protected_routes = set()
for i, line in enumerate(lines):
    if '@require_permission' in line:
        # Find the route decorator above it
        for j in range(max(0, i-5), i):
            if '@crm_bp.route' in lines[j]:
                protected_routes.add(j)
                break

print(f"Found {len(protected_routes)} already protected routes")

# Now add protection to routes that need it
# This is a complex task, so we'll do it manually for the remaining routes



