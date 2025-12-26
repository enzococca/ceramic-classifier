#!/usr/bin/env python3
"""
AI Schema Analyzer using Claude API
Automatically analyzes database schema and suggests pottery/ceramic table mappings
"""

import json
import re
from typing import Dict, Any, Optional
import requests


class AISchemaAnalyzer:
    """Uses Claude AI to analyze database schema and suggest mappings."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-sonnet-4-20250514"

    def analyze_schema(self, schema_info: Dict[str, Any], image_base_path: str) -> Dict[str, Any]:
        """
        Analyze database schema and suggest pottery table mappings.

        Args:
            schema_info: Database schema with tables, columns, and sample data
            image_base_path: Base path where images are stored

        Returns:
            Suggested configuration for pottery classification
        """
        prompt = self._build_analysis_prompt(schema_info, image_base_path)

        try:
            response = requests.post(
                self.api_url,
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": self.model,
                    "max_tokens": 4096,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get('content', [{}])[0].get('text', '')
                return self._parse_ai_response(content)
            else:
                return {
                    'success': False,
                    'error': f"API error: {response.status_code} - {response.text}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _build_analysis_prompt(self, schema_info: Dict[str, Any], image_base_path: str) -> str:
        """Build the prompt for schema analysis."""

        # Limit schema info to avoid token limits
        limited_schema = self._limit_schema_info(schema_info)

        return f"""You are an expert in archaeological databases. Analyze this database schema and identify:

1. The main table containing POTTERY/CERAMICS data
2. The table containing IMAGE/MEDIA references
3. How images are linked to pottery (junction table or direct field)
   - IMPORTANT: If there's a junction table, check if it has an entity_type field or similar
   - If so, identify the correct value (e.g., 'CERAMICA', 'POTTERY', 'ARTIFACT')
4. Relevant fields for pottery classification
5. The image filename pattern: often it's {{id_media}}_{{filename}}.png
6. Fields indicating if pottery is DECORATED (look for fields like exdeco, intdeco, decoration, decorated)
   - Analyze sample_data to understand which values indicate "decorated" (e.g., 'Yes', 'Si', true, 1)
   - If you find fields like exdeco and intdeco, include both in the filter with OR

DATABASE SCHEMA:
```json
{json.dumps(limited_schema, indent=2, default=str)}
```

BASE IMAGE PATH: {image_base_path}

Respond ONLY with valid JSON in the following format (no markdown, no comments):
{{
    "success": true,
    "pottery_table": {{
        "name": "pottery_table_name",
        "id_field": "primary_id_field",
        "fields": {{
            "site": "site_field_or_null",
            "area": "area_field_or_null",
            "us": "stratigraphic_unit_field_or_null",
            "form": "form_field_or_null",
            "decoration": "decoration_field_or_null",
            "decoration_type": "decoration_type_field_or_null",
            "fabric": "fabric_field_or_null",
            "period": "period_field_or_null",
            "description": "description_field_or_null"
        }}
    }},
    "media_table": {{
        "name": "media_table_name_or_null",
        "id_field": "media_id_field",
        "filename_field": "filename_field",
        "path_field": "path_field_or_null"
    }},
    "relation": {{
        "type": "direct|junction|embedded",
        "junction_table": "junction_table_name_or_null",
        "pottery_fk": "pottery_foreign_key",
        "media_fk": "media_foreign_key",
        "entity_type_field": "entity_type_field_if_present",
        "entity_type_value": "entity_type_value (e.g., CERAMICA, POTTERY)",
        "direct_image_field": "direct_image_field_if_embedded"
    }},
    "image_path_pattern": "{{media_id}}_{{filename}}.png (use placeholders with SQL field names)",
    "filter_decorated": {{
        "field": "exdeco",
        "value": "Yes",
        "operator": "=",
        "additional_condition": "OR p.intdeco = 'Yes' (if multiple decoration fields exist)"
    }},
    "confidence": 0.85,
    "notes": "any notes about the configuration"
}}

If you cannot identify a pottery table, respond with:
{{
    "success": false,
    "error": "Problem description",
    "suggestions": ["suggestion1", "suggestion2"]
}}
"""

    def _limit_schema_info(self, schema_info: Dict[str, Any], max_tables: int = 20) -> Dict[str, Any]:
        """Limit schema info to avoid token limits."""
        limited = {
            'database_type': schema_info.get('database_type'),
            'tables': {}
        }

        # Prioritize tables with pottery/ceramic/media related names
        priority_keywords = ['pottery', 'ceramic', 'ceramica', 'media', 'image', 'photo',
                           'foto', 'immagine', 'materiali', 'reperti', 'inventory',
                           'entity', 'relation', 'link', 'junction']

        tables = schema_info.get('tables', {})
        sorted_tables = sorted(
            tables.keys(),
            key=lambda t: -sum(1 for kw in priority_keywords if kw in t.lower())
        )

        for table in sorted_tables[:max_tables]:
            table_info = tables[table]
            limited['tables'][table] = {
                'columns': table_info.get('columns', [])[:30],  # Limit columns
                'sample_data': table_info.get('sample_data', [])[:2]  # Limit samples
            }

        return limited

    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract configuration."""
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                config = json.loads(json_match.group())
                return config
            else:
                return {
                    'success': False,
                    'error': 'No valid JSON found in AI response',
                    'raw_response': response_text[:500]
                }
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f'Invalid JSON in AI response: {e}',
                'raw_response': response_text[:500]
            }

    def generate_query(self, config: Dict[str, Any]) -> str:
        """Generate SQL query based on the analyzed configuration."""

        pottery = config.get('pottery_table', {})
        media = config.get('media_table', {})
        relation = config.get('relation', {})
        filter_dec = config.get('filter_decorated', {})

        # Build field list
        fields = [f'p.{pottery.get("id_field")} as id']

        field_mappings = pottery.get('fields', {})
        for alias, field in field_mappings.items():
            if field and field != 'null':
                fields.append(f'p.{field} as {alias}')

        if media.get('name'):
            if media.get('id_field'):
                fields.append(f'm.{media.get("id_field")} as media_id')
            if media.get('filename_field'):
                fields.append(f'm.{media.get("filename_field")} as filename')
            if media.get('path_field'):
                fields.append(f'm.{media.get("path_field")} as filepath')

        # Build FROM clause
        from_clause = f'FROM {pottery.get("name")} p'

        # Build JOIN clause based on relation type
        join_clause = ''
        entity_type_filter = ''
        if relation.get('entity_type_field') and relation.get('entity_type_value'):
            entity_type_filter = f" AND r.{relation.get('entity_type_field')} = '{relation.get('entity_type_value')}'"

        if relation.get('type') == 'junction' and relation.get('junction_table'):
            join_clause = f'''
            JOIN {relation.get("junction_table")} r ON r.{relation.get("pottery_fk")} = p.{pottery.get("id_field")}{entity_type_filter}
            JOIN {media.get("name")} m ON m.{media.get("id_field")} = r.{relation.get("media_fk")}
            '''
        elif relation.get('type') == 'direct' and media.get('name'):
            join_clause = f'''
            JOIN {media.get("name")} m ON m.{media.get("id_field")} = p.{relation.get("media_fk")}
            '''

        # Build WHERE clause for decorated filter
        where_clause = ''
        if filter_dec.get('field'):
            field = f"p.{filter_dec.get('field')}"
            operator = filter_dec.get('operator', '=')
            value = filter_dec.get('value')

            # Handle different operators
            if operator.upper() == 'IS NOT NULL':
                where_clause = f"WHERE {field} IS NOT NULL"
            elif operator.upper() == 'IS NULL':
                where_clause = f"WHERE {field} IS NULL"
            elif operator.upper() == 'LIKE':
                where_clause = f"WHERE {field} LIKE '%{value}%'"
            elif value is not None:
                # Quote string values
                if isinstance(value, str):
                    where_clause = f"WHERE {field} {operator} '{value}'"
                else:
                    where_clause = f"WHERE {field} {operator} {value}"
            # Backward compatibility: if 'condition' is a full SQL expression
            elif filter_dec.get('condition'):
                cond = filter_dec.get('condition')
                # Check if it's a full condition or just a value
                if any(op in cond.upper() for op in ['=', '>', '<', 'IS ', 'LIKE', 'IN ']):
                    where_clause = f"WHERE {cond}"
                else:
                    # Just a value, treat as = condition
                    where_clause = f"WHERE {field} = '{cond}'"

            # Handle additional conditions (e.g., OR p.intdeco = 'Yes')
            additional = filter_dec.get('additional_condition', '')
            if additional and 'OR' in additional.upper():
                # Extract the OR condition
                import re
                or_match = re.search(r'OR\s+p\.(\w+)\s*=\s*[\'"]?(\w+)[\'"]?', additional, re.IGNORECASE)
                if or_match:
                    add_field = or_match.group(1)
                    add_value = or_match.group(2)
                    where_clause = where_clause.replace('WHERE ', 'WHERE (') + f" OR p.{add_field} = '{add_value}')"

        # Use DISTINCT ON for PostgreSQL to get one image per pottery
        pottery_id = pottery.get("id_field")
        query = f"""
        SELECT DISTINCT ON (p.{pottery_id}) {', '.join(fields)}
        {from_clause}
        {join_clause}
        {where_clause}
        ORDER BY p.{pottery_id}
        """

        return query.strip()


def test_api_key(api_key: str) -> Dict[str, Any]:
    """Test if the API key is valid."""
    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 10,
                "messages": [{"role": "user", "content": "Hi"}]
            },
            timeout=10
        )

        if response.status_code == 200:
            return {'valid': True, 'message': 'API key is valid'}
        elif response.status_code == 401:
            return {'valid': False, 'message': 'Invalid API key'}
        else:
            return {'valid': False, 'message': f'API error: {response.status_code}'}

    except Exception as e:
        return {'valid': False, 'message': str(e)}
