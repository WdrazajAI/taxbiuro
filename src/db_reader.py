"""
Database reader module for Platnik ZUS data.
Connects to SQL Server using Windows Authentication.
"""

import pyodbc
from typing import List, Dict, Optional
from datetime import datetime


class DatabaseReader:
    """Reads ZUS declarations from Platnik SQL Server database."""

    def __init__(self, server: str, database: str, username: str = "", password: str = ""):
        """
        Initialize database connection parameters.

        Args:
            server: SQL Server instance name (e.g., 'localhost\\SQLEXPRESS' or '192.168.1.100')
            database: Database name
            username: SQL Server username (empty = Windows Authentication)
            password: SQL Server password (empty = Windows Authentication)
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.connection: Optional[pyodbc.Connection] = None

    def _get_connection_string(self) -> str:
        """
        Build connection string.

        If username/password provided -> SQL Server Authentication
        Otherwise -> Windows Authentication (Trusted Connection)
        """
        base = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database};"
        )

        # If username and password provided, use SQL Server Authentication
        if self.username and self.password:
            return base + f"UID={self.username};PWD={self.password};"
        else:
            # Windows Authentication (local)
            return base + "Trusted_Connection=yes;"

    def connect(self) -> bool:
        """
        Establish connection to the database.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            conn_str = self._get_connection_string()
            self.connection = pyodbc.connect(conn_str, timeout=10)
            return True
        except pyodbc.Error as e:
            print(f"Database connection error: {e}")
            return False

    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def test_connection(self) -> tuple[bool, str]:
        """
        Test database connection and return status.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            conn_str = self._get_connection_string()
            conn = pyodbc.connect(conn_str, timeout=10)
            conn.close()
            return True, "Połączenie z bazą danych OK"
        except pyodbc.Error as e:
            error_msg = str(e)
            if "Login failed" in error_msg:
                return False, "Błąd logowania - sprawdź uprawnienia Windows"
            elif "Cannot open database" in error_msg:
                return False, f"Nie można otworzyć bazy '{self.database}'"
            elif "server was not found" in error_msg or "network-related" in error_msg:
                return False, f"Serwer '{self.server}' nie odpowiada"
            else:
                return False, f"Błąd połączenia: {error_msg[:100]}"

    def get_available_periods(self) -> List[str]:
        """
        Get list of available periods from ZUSDRA table.

        Returns:
            List of period codes (e.g., ['022025', '012025', '122024'])
        """
        if not self.connection:
            if not self.connect():
                return []

        try:
            cursor = self.connection.cursor()
            query = """
                SELECT DISTINCT I_2_2OKRESDEKLAR
                FROM dbo.ZUSDRA
                WHERE I_2_2OKRESDEKLAR IS NOT NULL
                ORDER BY I_2_2OKRESDEKLAR DESC
            """
            cursor.execute(query)
            periods = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return periods
        except pyodbc.Error as e:
            print(f"Error fetching periods: {e}")
            return []

    def get_declarations_for_period(self, okres: str) -> List[Dict]:
        """
        Get all ZUS declarations for a given period.

        Args:
            okres: Period code in format 'MMRRRR' (e.g., '012025' for January 2025)

        Returns:
            List of dictionaries with declaration data
        """
        if not self.connection:
            if not self.connect():
                return []

        try:
            cursor = self.connection.cursor()
            query = """
                SELECT
                    II_1_NIP as NIP,
                    II_6_NAZWASKR as Firma,
                    I_2_2OKRESDEKLAR as Okres,
                    ISNULL(IV_32_KWSKSPOL, 0) as SkladkiSpoleczne,
                    ISNULL(VIII_1_KWNALSKLFP, 0) as FunduszPracy,
                    ISNULL(VIII_2_KWNALSKFGSP, 0) as FGSP,
                    COALESCE(IX_2_KWDOZAPLATY, IX_1_LSUMAKWDOZAPL, 0) as SumaDoZaplaty
                FROM dbo.ZUSDRA
                WHERE I_2_2OKRESDEKLAR = ?
                ORDER BY II_6_NAZWASKR
            """
            cursor.execute(query, okres)

            columns = [column[0] for column in cursor.description]
            results = []

            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                # Convert Decimal to float for JSON serialization
                for key in ['SkladkiSpoleczne', 'FunduszPracy', 'FGSP', 'SumaDoZaplaty']:
                    if record.get(key) is not None:
                        record[key] = float(record[key])
                results.append(record)

            cursor.close()
            return results

        except pyodbc.Error as e:
            print(f"Error fetching declarations: {e}")
            return []

    def get_declaration_count(self, okres: str) -> int:
        """
        Get count of declarations for a period.

        Args:
            okres: Period code in format 'MMRRRR'

        Returns:
            Number of declarations
        """
        if not self.connection:
            if not self.connect():
                return 0

        try:
            cursor = self.connection.cursor()
            query = """
                SELECT COUNT(*)
                FROM dbo.ZUSDRA
                WHERE I_2_2OKRESDEKLAR = ?
            """
            cursor.execute(query, okres)
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        except pyodbc.Error as e:
            print(f"Error counting declarations: {e}")
            return 0


def format_okres_readable(okres: str) -> str:
    """
    Convert period code to readable format.

    Args:
        okres: Period code 'MMRRRR' (e.g., '012025')

    Returns:
        Readable string (e.g., 'Styczeń 2025')
    """
    months = {
        '01': 'Styczeń', '02': 'Luty', '03': 'Marzec',
        '04': 'Kwiecień', '05': 'Maj', '06': 'Czerwiec',
        '07': 'Lipiec', '08': 'Sierpień', '09': 'Wrzesień',
        '10': 'Październik', '11': 'Listopad', '12': 'Grudzień'
    }

    if len(okres) >= 6:
        month = okres[:2]
        year = okres[2:6]
        month_name = months.get(month, month)
        return f"{month_name} {year}"
    return okres


def generate_periods(count: int = 12) -> List[str]:
    """
    Generate list of last N periods.

    Args:
        count: Number of periods to generate

    Returns:
        List of period codes in format 'MMRRRR'
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta

    periods = []
    current = datetime.now()

    for i in range(count):
        date = current - relativedelta(months=i)
        okres = f"{date.month:02d}{date.year}"
        periods.append(okres)

    return periods


if __name__ == "__main__":
    # Test connection
    reader = DatabaseReader("localhost\\SQLEXPRESS", "tax_testowa")
    success, message = reader.test_connection()
    print(f"Test: {message}")

    if success:
        periods = reader.get_available_periods()
        print(f"Dostępne okresy: {periods}")

        if periods:
            declarations = reader.get_declarations_for_period(periods[0])
            print(f"Deklaracji w {periods[0]}: {len(declarations)}")
            for decl in declarations[:3]:
                print(f"  - {decl['Firma']}: {decl['SumaDoZaplaty']} PLN")
