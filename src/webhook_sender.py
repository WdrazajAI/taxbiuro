"""
Webhook sender module for n8n integration.
Sends ZUS declaration data via HTTP POST.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class WebhookSender:
    """Sends ZUS data to n8n webhook."""

    def __init__(self, webhook_url: str, max_retries: int = 3, timeout: int = 30):
        """
        Initialize webhook sender.

        Args:
            webhook_url: n8n webhook URL
            max_retries: Number of retry attempts on failure
            timeout: Request timeout in seconds
        """
        self.webhook_url = webhook_url
        self.max_retries = max_retries
        self.timeout = timeout

    def prepare_payload(
        self,
        okres: str,
        okres_czytelny: str,
        deklaracje: List[Dict]
    ) -> Dict:
        """
        Prepare JSON payload for webhook.

        Args:
            okres: Period code (e.g., '012025')
            okres_czytelny: Readable period (e.g., 'Styczeń 2025')
            deklaracje: List of declarations from database

        Returns:
            Dictionary ready for JSON serialization
        """
        # Transform declarations to clean format
        klienci = []
        for decl in deklaracje:
            klienci.append({
                "nip": decl.get('NIP', '').strip(),
                "nazwa": decl.get('Firma', '').strip(),
                "skladki_spoleczne": decl.get('SkladkiSpoleczne', 0),
                "fundusz_pracy": decl.get('FunduszPracy', 0),
                "fgsp": decl.get('FGSP', 0),
                "suma_do_zaplaty": decl.get('SumaDoZaplaty', 0)
            })

        return {
            "okres": okres,
            "okres_czytelny": okres_czytelny,
            "data_eksportu": datetime.now().isoformat(),
            "liczba_klientow": len(klienci),
            "klienci": klienci
        }

    def send(
        self,
        okres: str,
        okres_czytelny: str,
        deklaracje: List[Dict],
        progress_callback: Optional[callable] = None
    ) -> Tuple[bool, str]:
        """
        Send data to n8n webhook with retry logic.

        Args:
            okres: Period code
            okres_czytelny: Readable period string
            deklaracje: List of declarations from database
            progress_callback: Optional callback for progress updates

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.webhook_url:
            return False, "Brak skonfigurowanego URL webhooka"

        if not deklaracje:
            return False, "Brak danych do wysłania"

        payload = self.prepare_payload(okres, okres_czytelny, deklaracje)

        for attempt in range(1, self.max_retries + 1):
            try:
                if progress_callback:
                    progress_callback(f"Próba {attempt}/{self.max_retries}...")

                response = requests.post(
                    self.webhook_url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=self.timeout
                )

                if response.status_code == 200:
                    return True, f"Wysłano pomyślnie! ({len(deklaracje)} klientów)"

                elif response.status_code == 404:
                    return False, "Webhook nie znaleziony (404) - sprawdź URL"

                elif response.status_code == 500:
                    if attempt < self.max_retries:
                        time.sleep(2 ** attempt)
                        continue
                    return False, f"Błąd serwera n8n (500)"

                else:
                    return False, f"Nieoczekiwana odpowiedź: {response.status_code}"

            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    if progress_callback:
                        progress_callback(f"Timeout - ponawiam ({attempt}/{self.max_retries})...")
                    time.sleep(2)
                    continue
                return False, "Timeout - serwer nie odpowiada"

            except requests.exceptions.ConnectionError:
                return False, "Brak połączenia z internetem"

            except requests.exceptions.RequestException as e:
                return False, f"Błąd sieci: {str(e)[:50]}"

        return False, "Przekroczono liczbę prób"

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test webhook connection with empty payload.

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.webhook_url:
            return False, "Brak URL webhooka w konfiguracji"

        try:
            test_payload = {
                "test": True,
                "timestamp": datetime.now().isoformat()
            }

            response = requests.post(
                self.webhook_url,
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                return True, "Połączenie z webhookiem OK"
            else:
                return False, f"Webhook odpowiedział kodem: {response.status_code}"

        except requests.exceptions.Timeout:
            return False, "Webhook nie odpowiada (timeout)"
        except requests.exceptions.ConnectionError:
            return False, "Brak połączenia z internetem"
        except Exception as e:
            return False, f"Błąd: {str(e)[:50]}"


def format_payload_preview(payload: Dict, max_clients: int = 3) -> str:
    """
    Format payload for human-readable preview.

    Args:
        payload: The payload dictionary
        max_clients: Maximum number of clients to show

    Returns:
        Formatted string for display
    """
    lines = [
        f"Okres: {payload.get('okres_czytelny', '')} ({payload.get('okres', '')})",
        f"Data eksportu: {payload.get('data_eksportu', '')[:19]}",
        f"Liczba klientów: {payload.get('liczba_klientow', 0)}",
        "",
        "Klienci:"
    ]

    klienci = payload.get('klienci', [])
    for i, klient in enumerate(klienci[:max_clients]):
        lines.append(f"  {i+1}. {klient.get('nazwa', 'N/A')}")
        lines.append(f"     NIP: {klient.get('nip', 'N/A')}")
        lines.append(f"     Suma do zapłaty: {klient.get('suma_do_zaplaty', 0):.2f} PLN")

    if len(klienci) > max_clients:
        lines.append(f"  ... i {len(klienci) - max_clients} więcej")

    return "\n".join(lines)
