#!/usr/bin/env python3
"""
Universal Database Connector
Supports: PostgreSQL, MySQL, SQLite, Oracle, MongoDB, CouchDB, Excel, CSV
"""

import os
import re
import json
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal
import traceback


def sanitize_value(value):
    """Convert non-JSON-serializable values to strings."""
    if value is None:
        return None
    if isinstance(value, (memoryview, bytes)):
        return f"<binary:{len(value)} bytes>"
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if hasattr(value, '__geo_interface__'):  # GeoJSON
        return "<geometry>"
    # Handle pandas/numpy NaN
    try:
        import math
        if isinstance(value, float) and math.isnan(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def sanitize_row(row_dict):
    """Sanitize all values in a row dictionary."""
    return {k: sanitize_value(v) for k, v in row_dict.items()}


class DatabaseConnector(ABC):
    """Abstract base class for database connectors."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to the database."""
        pass

    @abstractmethod
    def disconnect(self):
        """Close the database connection."""
        pass

    @abstractmethod
    def get_tables(self) -> List[str]:
        """Get list of tables/collections in the database."""
        pass

    @abstractmethod
    def get_columns(self, table: str) -> List[Dict[str, str]]:
        """Get columns and their types for a table."""
        pass

    @abstractmethod
    def get_sample_data(self, table: str, limit: int = 5) -> List[Dict]:
        """Get sample rows from a table."""
        pass

    @abstractmethod
    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        """Execute a query and return results."""
        pass

    def get_schema_info(self) -> Dict[str, Any]:
        """Get complete schema information for AI analysis."""
        schema = {
            'database_type': self.__class__.__name__.replace('Connector', ''),
            'tables': {}
        }

        for table in self.get_tables():
            schema['tables'][table] = {
                'columns': self.get_columns(table),
                'sample_data': self.get_sample_data(table, limit=3)
            }

        return schema


class PostgreSQLConnector(DatabaseConnector):
    """PostgreSQL database connector."""

    def connect(self) -> bool:
        try:
            import psycopg2
            self.connection = psycopg2.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 5432),
                database=self.config.get('database'),
                user=self.config.get('user'),
                password=self.config.get('password')
            )
            return True
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def get_tables(self) -> List[str]:
        cur = self.connection.cursor()
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        return [row[0] for row in cur.fetchall()]

    def get_columns(self, table: str) -> List[Dict[str, str]]:
        cur = self.connection.cursor()
        cur.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table,))
        return [{'name': row[0], 'type': row[1], 'nullable': row[2]} for row in cur.fetchall()]

    def get_sample_data(self, table: str, limit: int = 5) -> List[Dict]:
        cur = self.connection.cursor()
        cur.execute(f'SELECT * FROM "{table}" LIMIT %s', (limit,))
        columns = [desc[0] for desc in cur.description]
        return [sanitize_row(dict(zip(columns, row))) for row in cur.fetchall()]

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        cur = self.connection.cursor()
        cur.execute(query, params or ())
        columns = [desc[0] for desc in cur.description]
        return [sanitize_row(dict(zip(columns, row))) for row in cur.fetchall()]


class MySQLConnector(DatabaseConnector):
    """MySQL database connector."""

    def connect(self) -> bool:
        try:
            import mysql.connector
            self.connection = mysql.connector.connect(
                host=self.config.get('host', 'localhost'),
                port=self.config.get('port', 3306),
                database=self.config.get('database'),
                user=self.config.get('user'),
                password=self.config.get('password')
            )
            return True
        except Exception as e:
            print(f"MySQL connection error: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def get_tables(self) -> List[str]:
        cur = self.connection.cursor()
        cur.execute("SHOW TABLES")
        return [row[0] for row in cur.fetchall()]

    def get_columns(self, table: str) -> List[Dict[str, str]]:
        cur = self.connection.cursor()
        cur.execute(f"DESCRIBE `{table}`")
        return [{'name': row[0], 'type': row[1], 'nullable': row[2]} for row in cur.fetchall()]

    def get_sample_data(self, table: str, limit: int = 5) -> List[Dict]:
        cur = self.connection.cursor(dictionary=True)
        cur.execute(f"SELECT * FROM `{table}` LIMIT %s", (limit,))
        return [sanitize_row(row) for row in cur.fetchall()]

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        cur = self.connection.cursor(dictionary=True)
        cur.execute(query, params or ())
        return [sanitize_row(row) for row in cur.fetchall()]


class SQLiteConnector(DatabaseConnector):
    """SQLite database connector."""

    def connect(self) -> bool:
        try:
            import sqlite3
            self.connection = sqlite3.connect(self.config.get('database'))
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            print(f"SQLite connection error: {e}")
            return False

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def get_tables(self) -> List[str]:
        cur = self.connection.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [row[0] for row in cur.fetchall()]

    def get_columns(self, table: str) -> List[Dict[str, str]]:
        cur = self.connection.cursor()
        cur.execute(f"PRAGMA table_info('{table}')")
        return [{'name': row[1], 'type': row[2], 'nullable': 'YES' if not row[3] else 'NO'}
                for row in cur.fetchall()]

    def get_sample_data(self, table: str, limit: int = 5) -> List[Dict]:
        cur = self.connection.cursor()
        cur.execute(f"SELECT * FROM '{table}' LIMIT ?", (limit,))
        return [sanitize_row(dict(row)) for row in cur.fetchall()]

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        cur = self.connection.cursor()
        cur.execute(query, params or ())
        return [sanitize_row(dict(row)) for row in cur.fetchall()]


class MongoDBConnector(DatabaseConnector):
    """MongoDB database connector."""

    def connect(self) -> bool:
        try:
            from pymongo import MongoClient
            uri = self.config.get('uri', f"mongodb://{self.config.get('host', 'localhost')}:{self.config.get('port', 27017)}")
            self.client = MongoClient(uri)
            self.connection = self.client[self.config.get('database')]
            return True
        except Exception as e:
            print(f"MongoDB connection error: {e}")
            return False

    def disconnect(self):
        if hasattr(self, 'client'):
            self.client.close()

    def get_tables(self) -> List[str]:
        return self.connection.list_collection_names()

    def get_columns(self, table: str) -> List[Dict[str, str]]:
        # MongoDB is schemaless, infer from sample document
        sample = self.connection[table].find_one()
        if sample:
            return [{'name': k, 'type': type(v).__name__, 'nullable': 'YES'}
                    for k, v in sample.items()]
        return []

    def get_sample_data(self, table: str, limit: int = 5) -> List[Dict]:
        results = list(self.connection[table].find().limit(limit))
        # Convert ObjectId and other types to serializable values
        for doc in results:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        return [sanitize_row(doc) for doc in results]

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        # For MongoDB, query should be a JSON string with collection and filter
        query_obj = json.loads(query)
        collection = query_obj.get('collection')
        filter_query = query_obj.get('filter', {})
        projection = query_obj.get('projection')
        limit = query_obj.get('limit', 1000)

        cursor = self.connection[collection].find(filter_query, projection).limit(limit)
        results = list(cursor)
        for doc in results:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        return [sanitize_row(doc) for doc in results]


class ExcelConnector(DatabaseConnector):
    """Excel file connector using pandas."""

    def connect(self) -> bool:
        try:
            import pandas as pd
            self.file_path = self.config.get('file_path')
            self.excel_file = pd.ExcelFile(self.file_path)
            self.dataframes = {}
            return True
        except Exception as e:
            print(f"Excel connection error: {e}")
            return False

    def disconnect(self):
        self.dataframes = {}

    def get_tables(self) -> List[str]:
        return self.excel_file.sheet_names

    def get_columns(self, table: str) -> List[Dict[str, str]]:
        import pandas as pd
        if table not in self.dataframes:
            self.dataframes[table] = pd.read_excel(self.excel_file, sheet_name=table)
        df = self.dataframes[table]
        return [{'name': col, 'type': str(df[col].dtype), 'nullable': 'YES'}
                for col in df.columns]

    def get_sample_data(self, table: str, limit: int = 5) -> List[Dict]:
        import pandas as pd
        if table not in self.dataframes:
            self.dataframes[table] = pd.read_excel(self.excel_file, sheet_name=table)
        df = self.dataframes[table].head(limit)
        return [sanitize_row(row) for row in df.to_dict('records')]

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        import pandas as pd
        import re

        # Check if query is SQL-style or JSON
        if query.strip().upper().startswith('SELECT'):
            # Parse SQL-style query
            return self._execute_sql_style_query(query)

        # Simple query parsing for Excel (sheet_name and optional filter)
        query_obj = json.loads(query)
        sheet = query_obj.get('sheet')
        if sheet not in self.dataframes:
            self.dataframes[sheet] = pd.read_excel(self.excel_file, sheet_name=sheet)
        df = self.dataframes[sheet]

        # Apply filters if specified
        filters = query_obj.get('filters', {})
        for col, value in filters.items():
            if col in df.columns:
                df = df[df[col] == value]

        return [sanitize_row(row) for row in df.to_dict('records')]

    def _execute_sql_style_query(self, query: str) -> List[Dict]:
        """Execute SQL-style query on Excel data using pandas."""
        import pandas as pd
        import re

        # Parse SQL query
        # Expected format: SELECT ... FROM sheet_name [WHERE conditions]
        query_upper = query.upper()

        # Extract FROM table name
        from_match = re.search(r'FROM\s+(\w+)', query_upper)
        if not from_match:
            raise ValueError("Cannot parse FROM clause in query")

        sheet = from_match.group(1)

        # Try to find the actual sheet name (case-insensitive)
        actual_sheet = None
        for sheet_name in self.excel_file.sheet_names:
            if sheet_name.upper() == sheet.upper():
                actual_sheet = sheet_name
                break

        if not actual_sheet:
            # Try to match just the first sheet if name doesn't match
            if len(self.excel_file.sheet_names) > 0:
                actual_sheet = self.excel_file.sheet_names[0]
            else:
                raise ValueError(f"Sheet '{sheet}' not found")

        # Load the sheet
        if actual_sheet not in self.dataframes:
            self.dataframes[actual_sheet] = pd.read_excel(self.excel_file, sheet_name=actual_sheet)

        df = self.dataframes[actual_sheet].copy()

        # Parse WHERE clause
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER BY|GROUP BY|$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1).strip()
            df = self._apply_where_clause(df, where_clause)

        # Parse SELECT columns and create aliases
        select_match = re.search(r'SELECT\s+(?:DISTINCT\s+(?:ON\s*\([^)]+\)\s+)?)?(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if select_match:
            select_part = select_match.group(1).strip()
            if select_part != '*':
                df = self._apply_select_columns(df, select_part)

        return [sanitize_row(row) for row in df.to_dict('records')]

    def _apply_where_clause(self, df, where_clause: str):
        """Apply WHERE clause conditions to DataFrame."""
        import pandas as pd

        # Handle OR conditions
        or_parts = re.split(r'\s+OR\s+', where_clause, flags=re.IGNORECASE)

        if len(or_parts) > 1:
            # Multiple OR conditions
            combined_mask = pd.Series([False] * len(df), index=df.index)
            for part in or_parts:
                mask = self._parse_condition(df, part.strip())
                if mask is not None:
                    combined_mask = combined_mask | mask
            return df[combined_mask]
        else:
            # Single condition or AND conditions
            and_parts = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)
            combined_mask = pd.Series([True] * len(df), index=df.index)
            for part in and_parts:
                mask = self._parse_condition(df, part.strip())
                if mask is not None:
                    combined_mask = combined_mask & mask
            return df[combined_mask]

    def _parse_condition(self, df, condition: str):
        """Parse a single condition and return a boolean mask."""
        import pandas as pd

        # Remove parentheses
        condition = condition.strip('()')

        # Match patterns like: p.column = 'value' or column = 'value'
        match = re.match(r"(?:\w+\.)?(\w+)\s*(=|!=|<>|>|<|>=|<=|LIKE)\s*'([^']*)'", condition, re.IGNORECASE)
        if match:
            col_name = match.group(1)
            operator = match.group(2).upper()
            value = match.group(3)

            # Find actual column name (case-insensitive)
            actual_col = None
            for c in df.columns:
                if c.upper() == col_name.upper():
                    actual_col = c
                    break

            if actual_col is None:
                print(f"Warning: Column '{col_name}' not found in DataFrame")
                return None

            if operator == '=':
                return df[actual_col].astype(str).str.strip() == value
            elif operator in ('!=', '<>'):
                return df[actual_col].astype(str).str.strip() != value
            elif operator == 'LIKE':
                pattern = value.replace('%', '.*')
                return df[actual_col].astype(str).str.contains(pattern, case=False, na=False, regex=True)

        return None

    def _apply_select_columns(self, df, select_part: str):
        """Apply SELECT column list and aliases."""
        import pandas as pd

        columns = []
        aliases = {}

        # Split by comma, handling potential nested expressions
        parts = re.split(r',\s*(?![^()]*\))', select_part)

        for part in parts:
            part = part.strip()
            # Match: column AS alias or p.column as alias
            as_match = re.match(r"(?:\w+\.)?(\w+)\s+[Aa][Ss]\s+(\w+)", part)
            if as_match:
                col_name = as_match.group(1)
                alias = as_match.group(2)

                # Find actual column
                for c in df.columns:
                    if c.upper() == col_name.upper():
                        columns.append(c)
                        aliases[c] = alias
                        break
            else:
                # Simple column reference: p.column or column
                col_match = re.match(r"(?:\w+\.)?(\w+)", part)
                if col_match:
                    col_name = col_match.group(1)
                    for c in df.columns:
                        if c.upper() == col_name.upper():
                            columns.append(c)
                            break

        if columns:
            result_df = df[columns].copy()
            if aliases:
                result_df = result_df.rename(columns=aliases)
            return result_df

        return df


class CSVConnector(DatabaseConnector):
    """CSV file connector using pandas."""

    def connect(self) -> bool:
        try:
            import pandas as pd
            self.file_path = self.config.get('file_path')

            if os.path.isdir(self.file_path):
                # Directory with multiple CSV files
                self.dataframes = {}
                for f in os.listdir(self.file_path):
                    if f.endswith('.csv'):
                        name = f.replace('.csv', '')
                        self.dataframes[name] = pd.read_csv(os.path.join(self.file_path, f))
            else:
                # Single CSV file
                name = Path(self.file_path).stem
                self.dataframes = {name: pd.read_csv(self.file_path)}
            return True
        except Exception as e:
            print(f"CSV connection error: {e}")
            return False

    def disconnect(self):
        self.dataframes = {}

    def get_tables(self) -> List[str]:
        return list(self.dataframes.keys())

    def get_columns(self, table: str) -> List[Dict[str, str]]:
        df = self.dataframes.get(table)
        if df is not None:
            return [{'name': col, 'type': str(df[col].dtype), 'nullable': 'YES'}
                    for col in df.columns]
        return []

    def get_sample_data(self, table: str, limit: int = 5) -> List[Dict]:
        df = self.dataframes.get(table)
        if df is not None:
            return [sanitize_row(row) for row in df.head(limit).to_dict('records')]
        return []

    def execute_query(self, query: str, params: tuple = None) -> List[Dict]:
        import re

        # Check if query is SQL-style or JSON
        if query.strip().upper().startswith('SELECT'):
            # Parse SQL-style query
            return self._execute_sql_style_query(query)

        query_obj = json.loads(query)
        table = query_obj.get('table')
        df = self.dataframes.get(table)
        if df is None:
            return []

        filters = query_obj.get('filters', {})
        for col, value in filters.items():
            if col in df.columns:
                df = df[df[col] == value]

        return [sanitize_row(row) for row in df.to_dict('records')]

    def _execute_sql_style_query(self, query: str) -> List[Dict]:
        """Execute SQL-style query on CSV data using pandas."""
        import pandas as pd
        import re

        query_upper = query.upper()

        # Extract FROM table name
        from_match = re.search(r'FROM\s+(\w+)', query_upper)
        if not from_match:
            raise ValueError("Cannot parse FROM clause in query")

        table = from_match.group(1)

        # Try to find the actual table name (case-insensitive)
        actual_table = None
        for table_name in self.dataframes.keys():
            if table_name.upper() == table.upper():
                actual_table = table_name
                break

        if not actual_table:
            if len(self.dataframes) > 0:
                actual_table = list(self.dataframes.keys())[0]
            else:
                raise ValueError(f"Table '{table}' not found")

        df = self.dataframes[actual_table].copy()

        # Parse WHERE clause
        where_match = re.search(r'WHERE\s+(.+?)(?:ORDER BY|GROUP BY|$)', query, re.IGNORECASE | re.DOTALL)
        if where_match:
            where_clause = where_match.group(1).strip()
            df = self._apply_where_clause(df, where_clause)

        # Parse SELECT columns
        select_match = re.search(r'SELECT\s+(?:DISTINCT\s+(?:ON\s*\([^)]+\)\s+)?)?(.+?)\s+FROM', query, re.IGNORECASE | re.DOTALL)
        if select_match:
            select_part = select_match.group(1).strip()
            if select_part != '*':
                df = self._apply_select_columns(df, select_part)

        return [sanitize_row(row) for row in df.to_dict('records')]

    def _apply_where_clause(self, df, where_clause: str):
        """Apply WHERE clause conditions to DataFrame."""
        import pandas as pd

        or_parts = re.split(r'\s+OR\s+', where_clause, flags=re.IGNORECASE)

        if len(or_parts) > 1:
            combined_mask = pd.Series([False] * len(df), index=df.index)
            for part in or_parts:
                mask = self._parse_condition(df, part.strip())
                if mask is not None:
                    combined_mask = combined_mask | mask
            return df[combined_mask]
        else:
            and_parts = re.split(r'\s+AND\s+', where_clause, flags=re.IGNORECASE)
            combined_mask = pd.Series([True] * len(df), index=df.index)
            for part in and_parts:
                mask = self._parse_condition(df, part.strip())
                if mask is not None:
                    combined_mask = combined_mask & mask
            return df[combined_mask]

    def _parse_condition(self, df, condition: str):
        """Parse a single condition and return a boolean mask."""
        condition = condition.strip('()')
        match = re.match(r"(?:\w+\.)?(\w+)\s*(=|!=|<>|>|<|>=|<=|LIKE)\s*'([^']*)'", condition, re.IGNORECASE)
        if match:
            col_name = match.group(1)
            operator = match.group(2).upper()
            value = match.group(3)

            actual_col = None
            for c in df.columns:
                if c.upper() == col_name.upper():
                    actual_col = c
                    break

            if actual_col is None:
                return None

            if operator == '=':
                return df[actual_col].astype(str).str.strip() == value
            elif operator in ('!=', '<>'):
                return df[actual_col].astype(str).str.strip() != value
            elif operator == 'LIKE':
                pattern = value.replace('%', '.*')
                return df[actual_col].astype(str).str.contains(pattern, case=False, na=False, regex=True)

        return None

    def _apply_select_columns(self, df, select_part: str):
        """Apply SELECT column list and aliases."""
        columns = []
        aliases = {}
        parts = re.split(r',\s*(?![^()]*\))', select_part)

        for part in parts:
            part = part.strip()
            as_match = re.match(r"(?:\w+\.)?(\w+)\s+[Aa][Ss]\s+(\w+)", part)
            if as_match:
                col_name = as_match.group(1)
                alias = as_match.group(2)
                for c in df.columns:
                    if c.upper() == col_name.upper():
                        columns.append(c)
                        aliases[c] = alias
                        break
            else:
                col_match = re.match(r"(?:\w+\.)?(\w+)", part)
                if col_match:
                    col_name = col_match.group(1)
                    for c in df.columns:
                        if c.upper() == col_name.upper():
                            columns.append(c)
                            break

        if columns:
            result_df = df[columns].copy()
            if aliases:
                result_df = result_df.rename(columns=aliases)
            return result_df

        return df


# Connector factory
CONNECTOR_TYPES = {
    'postgresql': PostgreSQLConnector,
    'mysql': MySQLConnector,
    'sqlite': SQLiteConnector,
    'mongodb': MongoDBConnector,
    'excel': ExcelConnector,
    'csv': CSVConnector,
}


def create_connector(db_type: str, config: Dict[str, Any]) -> Optional[DatabaseConnector]:
    """Factory function to create database connectors."""
    connector_class = CONNECTOR_TYPES.get(db_type.lower())
    if connector_class:
        return connector_class(config)
    raise ValueError(f"Unsupported database type: {db_type}")


def test_connection(db_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Test database connection and return schema info."""
    try:
        connector = create_connector(db_type, config)
        if connector.connect():
            tables = connector.get_tables()
            connector.disconnect()
            return {
                'success': True,
                'tables': tables,
                'message': f'Connected successfully. Found {len(tables)} tables.'
            }
        return {'success': False, 'message': 'Connection failed'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
