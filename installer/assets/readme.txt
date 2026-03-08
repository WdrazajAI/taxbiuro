╔══════════════════════════════════════════════════════════════════╗
║              PLATNIK ZUS EXPORTER v1.0.0                         ║
║                                                                  ║
║     Automatyczny eksport składek ZUS do systemu n8n              ║
╚══════════════════════════════════════════════════════════════════╝

OPIS APLIKACJI
--------------
Aplikacja pozwala na automatyczne pobieranie informacji o składkach
ZUS z bazy danych programu Płatnik i wysyłanie ich do systemu
automatyzacji n8n.

Dzięki temu możesz zautomatyzować:
• Wysyłkę powiadomień e-mail do klientów o składkach
• Generowanie raportów miesięcznych
• Integrację z systemami księgowymi


WYMAGANIA SYSTEMOWE
-------------------
• Windows 10/11 (64-bit)
• Program Płatnik z bazą SQL Server
• Dostęp sieciowy do bazy danych
• Połączenie internetowe (dla webhooka)


INSTALACJA
----------
1. Uruchom instalator jako administrator
2. Postępuj zgodnie z instrukcjami na ekranie
3. Sterownik ODBC zostanie zainstalowany automatycznie


KONFIGURACJA (PO INSTALACJI)
----------------------------
1. Uruchom aplikację "Platnik ZUS Exporter"
2. Kliknij ikonę ⚙ (ustawienia) w prawym górnym rogu
3. Wypełnij dane połączenia:

   SERWER SQL:
   • Lokalny: localhost\SQLEXPRESS
   • Sieciowy: 192.168.1.100 lub nazwa_komputera\SQLEXPRESS

   BAZA DANYCH:
   • Domyślnie: tax_testowa (sprawdź w Płatniku)

   WEBHOOK URL:
   • Wklej URL z n8n (np. https://app.n8n.cloud/webhook/xxx)

4. Kliknij "Test połączenia"
5. Zapisz konfigurację


UŻYTKOWANIE
-----------
1. Wybierz okres rozliczeniowy z listy
2. Sprawdź podgląd danych
3. Kliknij "Wyślij do n8n"


ROZWIĄZYWANIE PROBLEMÓW
-----------------------
• Błąd połączenia z bazą:
  → Sprawdź czy Płatnik jest uruchomiony
  → Sprawdź dane serwera SQL w konfiguracji
  → Upewnij się że SQL Server pozwala na połączenia TCP/IP

• Błąd ODBC:
  → Uruchom instalator ponownie
  → Lub pobierz sterownik: https://go.microsoft.com/fwlink/?linkid=2249004


KONTAKT I WSPARCIE
------------------
E-mail: kontakt@wdrazaj.ai
Strona: https://wdrazaj.ai

