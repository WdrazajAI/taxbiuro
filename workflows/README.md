# Workflow: Składki ZUS - wysyłka e-maili

## Overview
This n8n workflow automates sending ZUS contribution notification emails to clients.

## Workflow Description

**Name:** Składki ZUS - wysyłka e-maili
**Trigger:** Webhook (POST)
**Instance:** https://wdrazajai.app.n8n.cloud

## Input Data Structure

The workflow expects a POST request to the webhook with the following JSON structure:

```json
{
  "okres": "202402",
  "okres_czytelny": "Luty 2024",
  "data_eksportu": "2024-03-01",
  "liczba_klientow": 10,
  "klienci": [
    {
      "nip": "1234567890",
      "nazwa": "Example Sp. z o.o.",
      "suma_do_zaplaty": "1234.56"
    }
  ]
}
```

## Workflow Nodes

### 1. Webhook - Dane ZUS
- **Type:** Webhook (POST)
- **Path:** `/zus-skladki-powiadomienia`
- **Purpose:** Receives ZUS contribution data

### 2. Loop Over Items
- **Type:** Split Out
- **Field:** `klienci`
- **Purpose:** Iterate through each client

### 3. Google Sheets - Lookup Email
- **Type:** Google Sheets
- **Operation:** Lookup
- **Lookup Column:** NIP
- **Purpose:** Find client email and active status
- **Required Columns in Sheet:**
  - `NIP` - Client tax ID
  - `Email` - Client email address
  - `Aktywny` - Active status ("TAK" or "NIE")
  - `Nazwa` - Company name (optional, falls back to webhook data)

### 4. IF - Aktywny
- **Type:** IF
- **Condition:** `Aktywny == "TAK"`
- **Purpose:** Only send emails to active clients

### 5. Set - Prepare Email Data
- **Type:** Set
- **Purpose:** Combine webhook data with Google Sheets lookup result
- **Fields Set:**
  - `nip`
  - `nazwa`
  - `suma_do_zaplaty`
  - `email`
  - `okres`
  - `okres_czytelny`
  - `data_eksportu`

### 6. Send Email
- **Type:** Email Send
- **Subject:** `Składki ZUS za {okres_czytelny}`
- **Email Type:** HTML
- **Purpose:** Send formatted email with ZUS contribution details

### 7. NoOp - Skip Inactive
- **Type:** No Operation
- **Purpose:** Pass through for inactive clients (no email sent)

### 8. Merge - Collect Results
- **Type:** Merge
- **Purpose:** Combine results from both branches (sent/skipped)

### 9. Webhook Response
- **Type:** Respond to Webhook
- **Purpose:** Return success response to caller

### 10. Error Trigger
- **Type:** Error Trigger
- **Purpose:** Catch any workflow errors

### 11. Send Error Notification
- **Type:** Email Send
- **Purpose:** Notify admin when errors occur

## Environment Variables Required

Set these in n8n instance settings:

```
GOOGLE_SHEETS_DOCUMENT_ID=<your-google-sheets-id>
GOOGLE_SHEETS_SHEET_NAME=Klienci
GOOGLE_SHEETS_CREDENTIAL_ID=<n8n-credential-id>
SMTP_CREDENTIAL_ID=<n8n-smtp-credential-id>
EMAIL_FROM=biuro@taxbiuro.pl
ERROR_EMAIL=admin@taxbiuro.pl
```

## Credentials Required

1. **Google Sheets OAuth2**
   - Permission: Read access to the client spreadsheet
   - Columns required: NIP, Email, Aktywny, Nazwa

2. **SMTP**
   - For sending client emails and error notifications

## Email Template

The workflow sends an HTML email with:
- Header with period (okres_czytelny)
- Company name and NIP
- Amount to pay (suma_do_zaplaty)
- Professional styling with TaxBiuro branding

## Testing

### Sample Test Payload

```bash
curl -X POST https://wdrazajai.app.n8n.cloud/webhook/zus-skladki-powiadomienia \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## Error Handling

- **Error Trigger** catches all workflow errors
- **Error Notification** sends email to admin with:
  - Error message
  - Timestamp
  - Instructions to check n8n

## Workflow Logic Flow

```
Webhook
  ↓
Loop Over klienci[]
  ↓
Google Sheets Lookup (by NIP)
  ↓
IF Aktywny = "TAK"
  ├─ YES → Prepare Data → Send Email → Merge
  └─ NO  → Skip (NoOp) → Merge
       ↓
    Webhook Response
```

## Deployment

1. Upload workflow JSON to n8n instance
2. Configure Google Sheets credential
3. Configure SMTP credential
4. Set environment variables
5. Activate workflow
6. Test with sample payload

## Maintenance Notes

- Check Google Sheets permissions monthly
- Verify SMTP credentials are valid
- Monitor error notifications
- Review inactive client list periodically

## Tags
- ZUS
- Email
- TaxBiuro

---

**Created:** 2026-02-26
**Version:** 1.0
**Instance:** wdrazajai.app.n8n.cloud
