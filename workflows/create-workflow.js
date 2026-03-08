const fs = require('fs');

const workflow = {
  "name": "Składki ZUS - wysyłka e-maili",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "zus-skladki-powiadomienia",
        "responseMode": "responseNode",
        "options": {}
      },
      "id": "webhook-zus-input",
      "name": "Webhook - Dane ZUS",
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1.1,
      "position": [240, 300],
      "webhookId": "zus-skladki-webhook",
      "notes": "Receives POST with: okres, okres_czytelny, data_eksportu, liczba_klientow, klienci[]"
    },
    {
      "parameters": {
        "respondWith": "allIncomingItems",
        "options": {}
      },
      "id": "webhook-response",
      "name": "Webhook Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [1680, 300],
      "notes": "Returns success response to caller"
    },
    {
      "parameters": {
        "fieldToSplitOut": "klienci",
        "options": {}
      },
      "id": "split-clients",
      "name": "Loop Over Items",
      "type": "n8n-nodes-base.splitOut",
      "typeVersion": 1,
      "position": [460, 300],
      "notes": "Iterate through each client in klienci array"
    },
    {
      "parameters": {
        "operation": "lookup",
        "documentId": {
          "__rl": true,
          "value": "={{ $env.GOOGLE_SHEETS_DOCUMENT_ID }}",
          "mode": "id"
        },
        "sheetName": {
          "__rl": true,
          "value": "={{ $env.GOOGLE_SHEETS_SHEET_NAME || 'Klienci' }}",
          "mode": "name"
        },
        "lookupColumn": "NIP",
        "lookupValue": "={{ $json.nip }}",
        "options": {
          "returnAllMatches": "firstMatch"
        }
      },
      "id": "google-sheets-lookup",
      "name": "Google Sheets - Lookup Email",
      "type": "n8n-nodes-base.googleSheets",
      "typeVersion": 4,
      "position": [680, 300],
      "credentials": {
        "googleSheetsOAuth2Api": {
          "id": "={{ $env.GOOGLE_SHEETS_CREDENTIAL_ID }}",
          "name": "Google Sheets Account"
        }
      },
      "notes": "Find client details by NIP column"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.Aktywny }}",
              "operation": "equals",
              "value2": "TAK"
            }
          ]
        }
      },
      "id": "if-active",
      "name": "IF - Aktywny",
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [900, 300],
      "notes": "Check if client is active (Aktywny = TAK)"
    }
  ],
  "connections": {},
  "settings": {
    "executionOrder": "v1"
  },
  "tags": []
};

fs.writeFileSync('skladki-zus-wyslilka-emaili.json', JSON.stringify(workflow, null, 2));
console.log('Workflow file created');
