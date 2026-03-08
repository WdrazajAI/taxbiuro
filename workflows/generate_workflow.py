import json

workflow = {
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
        }
    ],
    "connections": {},
    "settings": {"executionOrder": "v1"},
    "tags": []
}

with open("skladki-zus-wyslilka-emaili.json", "w", encoding="utf-8") as f:
    json.dump(workflow, f, indent=2, ensure_ascii=False)

print("Basic workflow created")
