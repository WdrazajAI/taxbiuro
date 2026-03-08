# Deployment Guide: Składki ZUS - wysyłka e-maili

## Pre-Deployment Checklist

### 1. Credentials Setup
Before deploying, ensure you have the following credentials configured in your n8n instance:

#### Google Sheets OAuth2
- Go to n8n → Credentials → Add Credential → Google Sheets OAuth2 API
- Authorize with Google account that has access to the client spreadsheet
- Note the credential ID for environment variables

#### SMTP Email Account
- Go to n8n → Credentials → Add Credential → SMTP
- Configure your email server settings:
  - Host: `smtp.example.com`
  - Port: `587` (or `465` for SSL)
  - User: `biuro@taxbiuro.pl`
  - Password: `[your-smtp-password]`
  - Secure: `true`
- Note the credential ID

### 2. Google Sheets Preparation

Create or prepare a Google Sheet with the following structure:

| NIP        | Nazwa             | Email                  | Aktywny |
|------------|-------------------|------------------------|---------|
| 1234567890 | Example Sp. z o.o.| example@company.com    | TAK     |
| 0987654321 | Test Company Ltd. | test@testcompany.com   | NIE     |

**Required Columns:**
- `NIP` - Client tax identification number (must match webhook data)
- `Email` - Client email address for notifications
- `Aktywny` - Active status ("TAK" or "NIE")
- `Nazwa` - Company name (optional, will use webhook name if not found)

**Get the Google Sheets Document ID:**
From the URL: `https://docs.google.com/spreadsheets/d/[DOCUMENT_ID]/edit`

### 3. Environment Variables

Set these in n8n instance settings or workflow variables:

```
GOOGLE_SHEETS_DOCUMENT_ID=1ABcD...xyz123
GOOGLE_SHEETS_SHEET_NAME=Klienci
GOOGLE_SHEETS_CREDENTIAL_ID=[your-credential-id]
SMTP_CREDENTIAL_ID=[your-smtp-credential-id]
EMAIL_FROM=biuro@taxbiuro.pl
ERROR_EMAIL=admin@taxbiuro.pl
```

## Deployment Steps

### Option 1: Manual Upload (Recommended for First Time)

1. Log in to your n8n instance: https://wdrazajai.app.n8n.cloud
2. Click "Add workflow" → "Import from File"
3. Select `skladki-zus-wyslilka-emaili.json`
4. Review the imported nodes
5. Update credential IDs in:
   - Google Sheets - Lookup Email node
   - Send Email node
   - Send Error Notification node
6. Set environment variables (Settings → Variables)
7. Test with sample data (see below)
8. Activate the workflow

### Option 2: Using n8n API

```bash
# Set your n8n API key
export N8N_API_KEY="your-api-key"
export N8N_HOST="https://wdrazajai.app.n8n.cloud"

# Import workflow
curl -X POST "${N8N_HOST}/api/v1/workflows" \
  -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  -H "Content-Type: application/json" \
  -d @skladki-zus-wyslilka-emaili.json
```

### Option 3: Using n8n CLI (if available)

```bash
n8n import:workflow --input=skladki-zus-wyslilka-emaili.json
```

## Post-Deployment Configuration

### 1. Update Credential References

After importing, you need to link the actual credentials:

1. Open the workflow in n8n
2. Click on "Google Sheets - Lookup Email" node
3. Select your Google Sheets OAuth2 credential from the dropdown
4. Click on "Send Email" node
5. Select your SMTP credential from the dropdown
6. Click on "Send Error Notification" node  
7. Select the same SMTP credential
8. Save the workflow

### 2. Set Environment Variables

Go to Settings → Variables and add:

```
GOOGLE_SHEETS_DOCUMENT_ID = [your-google-sheets-id]
GOOGLE_SHEETS_SHEET_NAME = Klienci
EMAIL_FROM = biuro@taxbiuro.pl
ERROR_EMAIL = admin@taxbiuro.pl
```

### 3. Get Webhook URL

1. Open the workflow
2. Click on "Webhook - Dane ZUS" node
3. Copy the Production Webhook URL
4. It should be: `https://wdrazajai.app.n8n.cloud/webhook/zus-skladki-powiadomienia`

## Testing

### Test Data

```json
{
  "okres": "202402",
  "okres_czytelny": "Luty 2024",
  "data_eksportu": "2024-03-01",
  "liczba_klientow": 2,
  "klienci": [
    {
      "nip": "1234567890",
      "nazwa": "Test Firma Sp. z o.o.",
      "suma_do_zaplaty": "1500.00"
    },
    {
      "nip": "0987654321",
      "nazwa": "Another Company Ltd.",
      "suma_do_zaplaty": "2300.50"
    }
  ]
}
```

### Test Command

```bash
curl -X POST https://wdrazajai.app.n8n.cloud/webhook/zus-skladki-powiadomienia \
  -H "Content-Type: application/json" \
  -d '{
    "okres": "202402",
    "okres_czytelny": "Luty 2024",
    "data_eksportu": "2024-03-01",
    "liczba_klientow": 1,
    "klienci": [
      {
        "nip": "1234567890",
        "nazwa": "Test Firma",
        "suma_do_zaplaty": "1500.00"
      }
    ]
  }'
```

### Expected Results

1. Workflow executes successfully
2. For each client in `klienci` array:
   - Looks up email by NIP in Google Sheets
   - If `Aktywny = "TAK"` → sends email
   - If `Aktywny = "NIE"` → skips (NoOp)
3. Returns success response
4. If error occurs → sends notification to ERROR_EMAIL

### Verification Steps

1. Check n8n execution history for the workflow
2. Check email inbox for test email
3. Verify email contains correct data:
   - Subject: "Składki ZUS za Luty 2024"
   - Body includes company name, NIP, amount
4. Check for any errors in execution log

## Troubleshooting

### Common Issues

#### Issue: "Google Sheets credential not found"
**Solution:** Update the credential ID in the Google Sheets node to match your actual credential

#### Issue: "Document not found" error
**Solution:** 
- Verify GOOGLE_SHEETS_DOCUMENT_ID is correct
- Ensure the Google account has access to the sheet
- Check sheet name matches GOOGLE_SHEETS_SHEET_NAME

#### Issue: "Column NIP not found"
**Solution:** Ensure your Google Sheet has a column header exactly named "NIP" (case-sensitive)

#### Issue: "SMTP authentication failed"
**Solution:**
- Verify SMTP credentials are correct
- Check if 2FA is enabled (may need app-specific password)
- Verify SMTP server allows connections

#### Issue: No email received
**Solution:**
- Check if client has `Aktywny = "TAK"` in Google Sheets
- Verify email address in Google Sheets is correct
- Check spam/junk folder
- Review workflow execution log for errors

### Debug Mode

To enable detailed logging:
1. Open workflow
2. Go to Settings → Executions
3. Enable "Save execution data"
4. Enable "Save manual executions"
5. Run test and check execution details

## Monitoring

### Recommended Monitoring

1. **Daily**: Check execution history for failures
2. **Weekly**: Review error notification emails
3. **Monthly**: Verify Google Sheets permissions still valid

### Metrics to Track

- Total executions
- Success rate
- Number of emails sent
- Number of inactive clients skipped
- Error rate

## Maintenance

### Regular Tasks

- **Weekly**: Review inactive clients in Google Sheets
- **Monthly**: Update Google Sheets data
- **Quarterly**: Rotate SMTP credentials if needed
- **Yearly**: Review and update email template

### Backup

Export workflow regularly:
1. Open workflow in n8n
2. Click "..." menu → "Download"
3. Save JSON file with date: `skladki-zus-YYYY-MM-DD.json`

## Security Considerations

- Never commit credentials to git
- Use environment variables for sensitive data
- Restrict Google Sheets access to necessary accounts only
- Use strong SMTP passwords
- Enable 2FA on email accounts
- Monitor ERROR_EMAIL for security alerts

## Support

For issues or questions:
- Check n8n execution logs first
- Review this deployment guide
- Contact: admin@taxbiuro.pl

---

**Deployed:** [DATE]
**Version:** 1.0
**Last Updated:** 2026-02-26
