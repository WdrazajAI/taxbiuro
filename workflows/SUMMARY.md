# Workflow Summary: Składki ZUS - wysyłka e-maili

## Quick Facts

- **Workflow Name:** Składki ZUS - wysyłka e-maili
- **Type:** Webhook-triggered email automation
- **Total Nodes:** 11
- **Status:** Ready for deployment
- **File:** `skladki-zus-wyslilka-emaili.json`

## What This Workflow Does

Automates sending ZUS (Polish social security) contribution notifications to clients via email:

1. Receives ZUS contribution data via webhook (POST)
2. Iterates through list of clients
3. Looks up each client's email and active status in Google Sheets (by NIP)
4. Sends HTML email to active clients with contribution details
5. Skips inactive clients
6. Returns success response to webhook caller
7. Sends error notifications to admin if anything goes wrong

## Workflow Nodes

```
1. Webhook - Dane ZUS          [Trigger]
2. Loop Over Items             [Split klienci array]
3. Google Sheets - Lookup Email [Find email by NIP]
4. IF - Aktywny                [Check if active]
5. Set - Prepare Email Data    [Combine webhook + Sheets data]
6. Send Email                  [Send ZUS notification]
7. NoOp - Skip Inactive        [Pass through for inactive]
8. Merge - Collect Results     [Combine sent/skipped]
9. Webhook Response            [Return success]
10. Error Trigger              [Error handler]
11. Send Error Notification    [Notify admin on error]
```

## Files Created

```
TAXBIURO/workflows/
├── skladki-zus-wyslilka-emaili.json  # Main workflow file (deploy this)
├── README.md                          # Workflow documentation
├── DEPLOYMENT.md                      # Deployment guide
├── SUMMARY.md                         # This file
├── create_full_workflow.js            # Generator script (for reference)
└── [other helper scripts]
```

## Required Credentials

1. **Google Sheets OAuth2** - to read client database
2. **SMTP Account** - to send emails

## Required Environment Variables

```
GOOGLE_SHEETS_DOCUMENT_ID=<your-sheet-id>
GOOGLE_SHEETS_SHEET_NAME=Klienci
GOOGLE_SHEETS_CREDENTIAL_ID=<n8n-credential-id>
SMTP_CREDENTIAL_ID=<n8n-smtp-credential-id>
EMAIL_FROM=biuro@taxbiuro.pl
ERROR_EMAIL=admin@taxbiuro.pl
```

## Google Sheets Structure

| Column | Description | Example | Required |
|--------|-------------|---------|----------|
| NIP | Tax ID | 1234567890 | Yes |
| Email | Client email | client@company.com | Yes |
| Aktywny | Active status | TAK / NIE | Yes |
| Nazwa | Company name | Example Sp. z o.o. | No* |

*Falls back to webhook data if not provided

## Webhook Endpoint

After deployment, the webhook will be available at:

```
POST https://wdrazajai.app.n8n.cloud/webhook/zus-skladki-powiadomienia
```

## Sample Webhook Payload

```json
{
  "okres": "202402",
  "okres_czytelny": "Luty 2024",
  "data_eksportu": "2024-03-01",
  "liczba_klientow": 2,
  "klienci": [
    {
      "nip": "1234567890",
      "nazwa": "Example Sp. z o.o.",
      "suma_do_zaplaty": "1500.00"
    },
    {
      "nip": "0987654321",
      "nazwa": "Test Company Ltd.",
      "suma_do_zaplaty": "2300.50"
    }
  ]
}
```

## Email Template

The workflow sends a professional HTML email with:

- Blue header with period (e.g., "Składki ZUS za Luty 2024")
- Company name and NIP
- Billing period
- **Amount to pay** (prominently displayed)
- Footer with generation date
- TaxBiuro branding

## Next Steps

1. **Review** workflow file: `skladki-zus-wyslilka-emaili.json`
2. **Prepare** Google Sheets with client data (see README.md)
3. **Configure** credentials in n8n instance
4. **Deploy** workflow (see DEPLOYMENT.md)
5. **Test** with sample data
6. **Activate** workflow
7. **Monitor** execution logs

## Testing

Quick test command:

```bash
curl -X POST https://wdrazajai.app.n8n.cloud/webhook/zus-skladki-powiadomienia \
  -H "Content-Type: application/json" \
  -d @test-payload.json
```

## Monitoring

- Check n8n execution history daily
- Review error notifications sent to ERROR_EMAIL
- Verify emails are being received by clients
- Monitor Google Sheets permissions

## Support Documents

- **README.md** - Comprehensive workflow documentation
- **DEPLOYMENT.md** - Step-by-step deployment guide
- **SUMMARY.md** - This quick reference

## Version

- **Created:** 2026-02-26
- **Version:** 1.0
- **Status:** Production-ready
- **Instance:** wdrazajai.app.n8n.cloud

## Tags

`ZUS` `Email` `TaxBiuro` `Automation` `Notifications`

---

Ready for deployment to n8n instance!
