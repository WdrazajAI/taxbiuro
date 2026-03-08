# Składki ZUS - Workflow Files Index

## Main Files

### Production Workflow
- **skladki-zus-wyslilka-emaili.json** (9.8 KB)
  - The main n8n workflow file - DEPLOY THIS FILE
  - Contains all 11 nodes with complete configuration
  - Ready for import into n8n instance

### Test Data
- **test-payload.json** (0.3 KB)
  - Sample webhook payload for testing
  - Contains 3 test clients

## Documentation Files

### Quick Start
1. **SUMMARY.md** (4.4 KB)
   - Quick reference guide
   - Key facts and configuration
   - Perfect for getting started

2. **CHECKLIST.md** (1.9 KB)
   - Step-by-step deployment checklist
   - Pre/post deployment tasks
   - Sign-off sheet

### Detailed Guides
3. **README.md** (4.6 KB)
   - Complete workflow documentation
   - Node descriptions
   - Email template details
   - Testing instructions

4. **DEPLOYMENT.md** (7.3 KB)
   - Step-by-step deployment guide
   - Credential setup instructions
   - Troubleshooting section
   - Monitoring recommendations

## Helper Scripts (Reference Only)

- **create_full_workflow.js** - Node.js script that generated the workflow
- **build_workflow.js** - Helper script for workflow generation
- **generate_workflow.py** - Python helper script

## File Structure

```
workflows/
├── INDEX.md                              [This file]
├── SUMMARY.md                            [Quick reference]
├── README.md                             [Full documentation]
├── DEPLOYMENT.md                         [Deployment guide]
├── CHECKLIST.md                          [Deployment checklist]
├── skladki-zus-wyslilka-emaili.json     [MAIN WORKFLOW FILE]
├── test-payload.json                     [Test data]
└── [helper scripts...]
```

## Quick Start Guide

### 1. Read First
- SUMMARY.md - Get an overview
- README.md - Understand the workflow

### 2. Prepare
- CHECKLIST.md - Check prerequisites
- DEPLOYMENT.md - Review deployment steps

### 3. Deploy
- Import: skladki-zus-wyslilka-emaili.json
- Configure credentials
- Set environment variables

### 4. Test
- Use: test-payload.json
- Verify email delivery
- Check error handling

### 5. Activate
- Review execution logs
- Activate workflow
- Monitor performance

## Key Information

**Workflow Name:** Składki ZUS - wysyłka e-maili
**Total Nodes:** 11
**Webhook Path:** /zus-skladki-powiadomienia
**Instance:** https://wdrazajai.app.n8n.cloud

**Required Credentials:**
- Google Sheets OAuth2
- SMTP Account

**Required Variables:**
- GOOGLE_SHEETS_DOCUMENT_ID
- GOOGLE_SHEETS_SHEET_NAME
- GOOGLE_SHEETS_CREDENTIAL_ID
- SMTP_CREDENTIAL_ID
- EMAIL_FROM
- ERROR_EMAIL

## Tags

`ZUS` `Email` `TaxBiuro` `n8n` `Automation`

---

**Created:** 2026-02-26
**Status:** Production Ready
**Version:** 1.0
