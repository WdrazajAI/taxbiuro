# Deployment Checklist

## Pre-Deployment

- [ ] Google Sheets created with required columns (NIP, Email, Aktywny, Nazwa)
- [ ] Google Sheets populated with client data
- [ ] Google Sheets Document ID obtained
- [ ] Google OAuth2 credential created in n8n
- [ ] SMTP credential created in n8n
- [ ] Test email account verified
- [ ] Admin error email verified

## Deployment

- [ ] Log into n8n instance (wdrazajai.app.n8n.cloud)
- [ ] Import workflow file (skladki-zus-wyslilka-emaili.json)
- [ ] Update Google Sheets credential in node 3
- [ ] Update SMTP credential in node 6
- [ ] Update SMTP credential in node 11
- [ ] Set environment variables in n8n
- [ ] Save workflow
- [ ] Copy webhook URL

## Testing

- [ ] Test with single client payload
- [ ] Verify email received
- [ ] Test with active client (Aktywny = TAK)
- [ ] Test with inactive client (Aktywny = NIE)
- [ ] Test with multiple clients
- [ ] Test error handling (invalid NIP)
- [ ] Verify error notification sent to admin
- [ ] Check execution logs

## Activation

- [ ] Review all test results
- [ ] Fix any issues found
- [ ] Activate workflow in n8n
- [ ] Document webhook URL for integration
- [ ] Notify stakeholders workflow is live

## Post-Deployment

- [ ] Monitor first production run
- [ ] Verify emails are being sent
- [ ] Check for any errors
- [ ] Document any issues
- [ ] Set up regular monitoring schedule

## Documentation

- [ ] README.md reviewed
- [ ] DEPLOYMENT.md reviewed
- [ ] Webhook URL documented
- [ ] Google Sheets structure documented
- [ ] Environment variables documented
- [ ] Credentials documented (securely)

## Backup

- [ ] Workflow JSON backed up
- [ ] Google Sheets backed up
- [ ] Credentials documented (in password manager)

---

**Completed by:** _________________
**Date:** _________________
**Verified by:** _________________
