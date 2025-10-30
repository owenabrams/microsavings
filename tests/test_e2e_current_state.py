#!/usr/bin/env python3
"""
End-to-End Test for Current Application State
Tests the ACTUAL current database schema, ORM models, and frontend expectations
"""

import pytest
import json
import requests
import os
from datetime import datetime, timedelta
from decimal import Decimal


class TestCurrentApplicationState:
    """Test suite validating current app state (database + backend + frontend)"""

    def test_01_database_schema_group_members(self, client, auth_token):
        """Verify group_members table has all required columns"""
        # Create a test group first
        group_response = client.post(
            '/api/savings-groups',
            json={
                'name': 'Test Group',
                'district': 'Kampala',
                'parish': 'Central',
                'village': 'Nakasero',
                'formation_date': '2025-01-01'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert group_response.status_code in [200, 201], f"Failed to create group: {group_response.json}"
        group_id = group_response.json['data']['group']['id']

        # Try to create a member with ORM model fields
        member_response = client.post(
            f'/api/savings-groups/{group_id}/members',
            json={
                'name': 'John Doe',  # ORM expects this
                'gender': 'M',
                'phone': '+256701234567',  # ORM expects this
                'role': 'MEMBER',  # ORM expects this
                'is_active': True  # ORM expects this
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        # This test will FAIL if database doesn't have these columns
        # Expected: 201 Created
        # Actual: Will fail if columns missing
        print(f"Member creation response: {member_response.status_code}")
        print(f"Response: {member_response.json}")
        
        # If we get here, the columns exist
        assert member_response.status_code in [200, 201], \
            f"Failed to create member. Response: {member_response.json}"

    def test_02_database_schema_savings_groups(self, client, auth_token):
        """Verify savings_groups table has all required columns"""
        group_response = client.post(
            '/api/savings-groups',
            json={
                'name': 'Schema Test Group',
                'district': 'Kampala',
                'parish': 'Central',
                'village': 'Nakasero',
                'country': 'Uganda',  # ORM expects this
                'formation_date': '2024-01-01',  # ORM expects this
                'state': 'ACTIVE',  # ORM expects this (not status)
                'target_amount': 1000000,  # ORM expects this
                'max_members': 30  # ORM expects this
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        print(f"Group creation response: {group_response.status_code}")
        print(f"Response: {group_response.json}")
        
        # This test will FAIL if database doesn't have these columns
        assert group_response.status_code in [200, 201], \
            f"Failed to create group with ORM fields. Response: {group_response.json}"

    def test_03_frontend_expects_member_fields(self, client, auth_token):
        """Verify API returns fields that frontend expects"""
        # Get a group
        groups_response = client.get(
            '/api/savings-groups',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert groups_response.status_code == 200
        
        if groups_response.json['data']['groups']:
            group_id = groups_response.json['data']['groups'][0]['id']
            
            # Get members
            members_response = client.get(
                f'/api/savings-groups/{group_id}/members',
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            
            if members_response.status_code == 200 and members_response.json['data']['members']:
                member = members_response.json['data']['members'][0]
                
                # Frontend expects these fields (from GroupMembers.js)
                required_fields = [
                    'name',  # Line 359: {member.name}
                    'gender',  # Line 362: {member.gender}
                    'joined_date',  # Line 362: member.joined_date
                    'phone',  # Line 372: {member.phone}
                    'share_balance',  # Line 397: member.share_balance
                    'total_contributions',  # Line 400: member.total_contributions
                    'is_active',  # Line 405: member.is_active
                    'role'  # Line 922: {member.role}
                ]
                
                for field in required_fields:
                    assert field in member, \
                        f"Frontend expects '{field}' but API didn't return it. Member: {member}"

    def test_04_frontend_expects_group_fields(self, client, auth_token):
        """Verify API returns group fields that frontend expects"""
        groups_response = client.get(
            '/api/savings-groups',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert groups_response.status_code == 200
        
        if groups_response.json['data']['groups']:
            group = groups_response.json['data']['groups'][0]
            
            # Frontend expects these fields (from GroupOverview.js, GroupOversight.js)
            required_fields = [
                'name',  # Line 412: {group.name}
                'district',  # Line 421: {group.district}
                'parish',  # Line 423: {group.parish}
                'village',  # Line 423: {group.village}
                'formation_date',  # Line 85: group.formation_date
                'region',  # Line 99: {group.region}
                'status',  # Line 106: {group.status}
                'max_members',  # Line 431: {group.max_members}
                'member_count'  # Line 428: {group.member_count}
            ]
            
            for field in required_fields:
                assert field in group, \
                    f"Frontend expects '{field}' but API didn't return it. Group: {group}"

    def test_05_seeding_script_compatibility(self, client, auth_token):
        """Verify seeding script can create data with ORM model fields"""
        # The seeding script uses ORM models like:
        # GroupMember(group_id=group.id, user_id=user.id, name=name, gender=gender, phone=phone, role=role)
        # This test verifies the database supports this
        
        group_response = client.post(
            '/api/savings-groups',
            json={
                'name': 'Seeding Test Group',
                'district': 'Kampala',
                'parish': 'Central',
                'village': 'Nakasero'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        assert group_response.status_code in [200, 201]
        group_id = group_response.json['data']['group']['id']

        # Try to create multiple members like the seeding script does
        for i in range(3):
            member_response = client.post(
                f'/api/savings-groups/{group_id}/members',
                json={
                    'name': f'Member {i+1}',
                    'gender': 'M' if i % 2 == 0 else 'F',
                    'phone': f'+256701234{i:03d}',
                    'role': 'FOUNDER' if i == 0 else 'MEMBER'
                },
                headers={'Authorization': f'Bearer {auth_token}'}
            )
            assert member_response.status_code in [200, 201], \
                f"Failed to create member {i+1}. Response: {member_response.json}"

    def test_06_financial_tracking_fields(self, client, auth_token):
        """Verify financial tracking fields exist and work"""
        # Create group and member
        group_response = client.post(
            '/api/savings-groups',
            json={
                'name': 'Financial Test Group',
                'district': 'Kampala',
                'parish': 'Central',
                'village': 'Nakasero'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        group_id = group_response.json['data']['group']['id']

        member_response = client.post(
            f'/api/savings-groups/{group_id}/members',
            json={
                'name': 'Financial Test Member',
                'gender': 'M',
                'phone': '+256701234567',
                'role': 'MEMBER'
            },
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        member_id = member_response.json['data']['id']
        
        # Get member and verify financial fields
        get_response = client.get(
            f'/api/savings-groups/{group_id}/members/{member_id}',
            headers={'Authorization': f'Bearer {auth_token}'}
        )
        
        if get_response.status_code == 200:
            member = get_response.json['data']['member']
            # These fields should exist and be numeric
            assert 'share_balance' in member
            assert 'total_contributions' in member
            assert isinstance(member.get('share_balance'), (int, float, str))
            assert isinstance(member.get('total_contributions'), (int, float, str))


class APIClient:
    """HTTP client for testing against running Docker container"""
    def __init__(self, base_url='http://localhost:5001'):
        self.base_url = base_url
        self.session = requests.Session()

    def post(self, path, json=None, headers=None):
        """POST request"""
        url = f"{self.base_url}{path}"
        response = self.session.post(url, json=json, headers=headers)
        # Add json attribute for compatibility
        try:
            response.json = response.json()
        except:
            response.json = {}
        return response

    def get(self, path, headers=None):
        """GET request"""
        url = f"{self.base_url}{path}"
        response = self.session.get(url, headers=headers)
        # Add json attribute for compatibility
        try:
            response.json = response.json()
        except:
            response.json = {}
        return response


@pytest.fixture
def client():
    """Create API client for Docker container"""
    return APIClient(base_url=os.getenv('API_URL', 'http://localhost:5001'))


@pytest.fixture
def auth_token(client):
    """Get authentication token"""
    response = client.post(
        '/api/auth/login',
        json={'email': 'admin@savingsgroup.com', 'password': 'admin123'}
    )
    if response.status_code == 200:
        # API returns auth_token directly, not nested in data
        return response.json.get('auth_token') or response.json.get('data', {}).get('access_token')
    return None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

