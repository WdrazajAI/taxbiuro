const fs = require('fs');

const nodes = [];
const connections = {};

// Node 1: Webhook
nodes.push({
  parameters: {
    httpMethod: "POST",
    path: "zus-skladki-powiadomienia",
    responseMode: "responseNode",
    options: {}
  },
  id: "n1-webhook",
  name: "Webhook - Dane ZUS",
  type: "n8n-nodes-base.webhook",
  typeVersion: 1.1,
  position: [240, 300],
  webhookId: "zus-skladki",
  notes: "POST: okres, okres_czytelny, data_eksportu, liczba_klientow, klienci[]"
});

// Node 2: Split
nodes.push({
  parameters: { fieldToSplitOut: "klienci", options: {} },
  id: "n2-split",
  name: "Loop Over Items",
  type: "n8n-nodes-base.splitOut",
  typeVersion: 1,
  position: [460, 300],
  notes: "Iterate klienci array"
});

// Node 3: Google Sheets
nodes.push({
  parameters: {
    operation: "lookup",
    documentId: { __rl: true, value: "={{ $env.GOOGLE_SHEETS_DOCUMENT_ID }}", mode: "id" },
    sheetName: { __rl: true, value: "={{ $env.GOOGLE_SHEETS_SHEET_NAME || 'Klienci' }}", mode: "name" },
    lookupColumn: "NIP",
    lookupValue: "={{ $json.nip }}",
    options: { returnAllMatches: "firstMatch" }
  },
  id: "n3-sheets",
  name: "Google Sheets - Lookup Email",
  type: "n8n-nodes-base.googleSheets",
  typeVersion: 4,
  position: [680, 300],
  credentials: { googleSheetsOAuth2Api: { id: "={{ $env.GOOGLE_SHEETS_CREDENTIAL_ID }}", name: "Google Sheets" } },
  notes: "Lookup by NIP: Email, Aktywny"
});

// Node 4: IF
nodes.push({
  parameters: { conditions: { string: [{ value1: "={{ $json.Aktywny }}", operation: "equals", value2: "TAK" }] } },
  id: "n4-if",
  name: "IF - Aktywny",
  type: "n8n-nodes-base.if",
  typeVersion: 1,
  position: [900, 300],
  notes: "Aktywny = TAK?"
});

// Node 5: Set
nodes.push({
  parameters: {
    assignments: {
      assignments: [
        { id: "a1", name: "nip", value: "={{ $json.nip }}", type: "string" },
        { id: "a2", name: "nazwa", value: "={{ $json.Nazwa || $json.nazwa }}", type: "string" },
        { id: "a3", name: "suma_do_zaplaty", value: "={{ $json.suma_do_zaplaty }}", type: "string" },
        { id: "a4", name: "email", value: "={{ $json.Email || $json.email }}", type: "string" },
        { id: "a5", name: "okres", value: "={{ $('Webhook - Dane ZUS').first().json.okres }}", type: "string" },
        { id: "a6", name: "okres_czytelny", value: "={{ $('Webhook - Dane ZUS').first().json.okres_czytelny }}", type: "string" },
        { id: "a7", name: "data_eksportu", value: "={{ $('Webhook - Dane ZUS').first().json.data_eksportu }}", type: "string" }
      ]
    },
    options: {}
  },
  id: "n5-set",
  name: "Set - Prepare Email Data",
  type: "n8n-nodes-base.set",
  typeVersion: 3.2,
  position: [1120, 200],
  notes: "Combine data"
});

// Node 6: Send Email
const emailHTML = '<!DOCTYPE html><html><head><meta charset="utf-8"><style>body{font-family:Arial,sans-serif;line-height:1.6;color:#333}.container{max-width:600px;margin:0 auto;padding:20px}.header{background-color:#0066cc;color:white;padding:20px;text-align:center}.content{background-color:#f9f9f9;padding:20px;margin:20px 0}.amount{font-size:24px;font-weight:bold;color:#0066cc}.footer{font-size:12px;color:#666;margin-top:20px;padding-top:20px;border-top:1px solid #ddd}</style></head><body><div class="container"><div class="header"><h1>Składki ZUS za {{ $json.okres_czytelny }}</h1></div><div class="content"><p>Dzień dobry,</p><p>Informujemy o składkach ZUS dla firmy <strong>{{ $json.nazwa }}</strong> (NIP: {{ $json.nip }}).</p><p><strong>Okres rozliczeniowy:</strong> {{ $json.okres_czytelny }}</p><p class="amount">Suma do zapłaty: {{ $json.suma_do_zaplaty }} zł</p><p>W razie pytań prosimy o kontakt.</p><p>Pozdrawiamy,<br>Zespół TaxBiuro</p></div><div class="footer"><p>Wiadomość wygenerowana automatycznie dnia {{ $json.data_eksportu }}</p><p>Nie odpowiadaj na tego e-maila.</p></div></div></body></html>';

nodes.push({
  parameters: {
    fromEmail: "={{ $env.EMAIL_FROM || 'biuro@taxbiuro.pl' }}",
    toEmail: "={{ $json.email }}",
    subject: "=Składki ZUS za {{ $json.okres_czytelny }}",
    emailType: "html",
    message: "=" + emailHTML,
    options: {}
  },
  id: "n6-email",
  name: "Send Email",
  type: "n8n-nodes-base.emailSend",
  typeVersion: 2,
  position: [1340, 200],
  credentials: { smtp: { id: "={{ $env.SMTP_CREDENTIAL_ID }}", name: "SMTP" } },
  notes: "Send ZUS notification"
});

// Node 7: NoOp
nodes.push({
  parameters: {},
  id: "n7-noop",
  name: "NoOp - Skip Inactive",
  type: "n8n-nodes-base.noOp",
  typeVersion: 1,
  position: [1120, 400],
  notes: "Skip inactive"
});

// Node 8: Merge
nodes.push({
  parameters: { mode: "combine", combineBy: "combineAll" },
  id: "n8-merge",
  name: "Merge - Collect Results",
  type: "n8n-nodes-base.merge",
  typeVersion: 2.1,
  position: [1500, 300],
  notes: "Combine results"
});

// Node 9: Webhook Response
nodes.push({
  parameters: { respondWith: "allIncomingItems", options: {} },
  id: "n9-response",
  name: "Webhook Response",
  type: "n8n-nodes-base.respondToWebhook",
  typeVersion: 1,
  position: [1680, 300],
  notes: "Return response"
});

// Node 10: Error Trigger
nodes.push({
  parameters: {},
  id: "n10-error",
  name: "Error Trigger",
  type: "n8n-nodes-base.errorTrigger",
  typeVersion: 1,
  position: [240, 500],
  notes: "Error handler"
});

// Node 11: Error Email
nodes.push({
  parameters: {
    fromEmail: "={{ $env.EMAIL_FROM || 'biuro@taxbiuro.pl' }}",
    toEmail: "={{ $env.ERROR_EMAIL || 'admin@taxbiuro.pl' }}",
    subject: "=BŁĄD: Workflow ZUS - {{ $json.error.message }}",
    emailType: "text",
    message: "=Wystąpił błąd podczas wysyłki e-maili ZUS.\n\nKomunikat błędu:\n{{ $json.error.message }}\n\nCzas: {{ $now }}",
    options: {}
  },
  id: "n11-error-email",
  name: "Send Error Notification",
  type: "n8n-nodes-base.emailSend",
  typeVersion: 2,
  position: [460, 500],
  credentials: { smtp: { id: "={{ $env.SMTP_CREDENTIAL_ID }}", name: "SMTP" } },
  notes: "Notify admin"
});

// Define connections
connections["Webhook - Dane ZUS"] = { main: [[{ node: "Loop Over Items", type: "main", index: 0 }]] };
connections["Loop Over Items"] = { main: [[{ node: "Google Sheets - Lookup Email", type: "main", index: 0 }]] };
connections["Google Sheets - Lookup Email"] = { main: [[{ node: "IF - Aktywny", type: "main", index: 0 }]] };
connections["IF - Aktywny"] = {
  main: [
    [{ node: "Set - Prepare Email Data", type: "main", index: 0 }],
    [{ node: "NoOp - Skip Inactive", type: "main", index: 0 }]
  ]
};
connections["Set - Prepare Email Data"] = { main: [[{ node: "Send Email", type: "main", index: 0 }]] };
connections["Send Email"] = { main: [[{ node: "Merge - Collect Results", type: "main", index: 0 }]] };
connections["NoOp - Skip Inactive"] = { main: [[{ node: "Merge - Collect Results", type: "main", index: 1 }]] };
connections["Merge - Collect Results"] = { main: [[{ node: "Webhook Response", type: "main", index: 0 }]] };
connections["Error Trigger"] = { main: [[{ node: "Send Error Notification", type: "main", index: 0 }]] };

const workflow = {
  name: "Składki ZUS - wysyłka e-maili",
  nodes: nodes,
  connections: connections,
  settings: { executionOrder: "v1" },
  staticData: null,
  tags: [
    { name: "ZUS", id: "zus-tag" },
    { name: "Email", id: "email-tag" },
    { name: "TaxBiuro", id: "taxbiuro-tag" }
  ],
  pinData: {},
  versionId: "1"
};

fs.writeFileSync('skladki-zus-wyslilka-emaili.json', JSON.stringify(workflow, null, 2));
console.log('Complete workflow created successfully!');
console.log('File: skladki-zus-wyslilka-emaili.json');
console.log('Nodes:', workflow.nodes.length);
