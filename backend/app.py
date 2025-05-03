# app.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
import uuid
import pandas as pd
import io

# Google Sheets API imports
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__, static_folder='../dist', static_url_path='/')
CORS(app)

# Configuration for Google Sheets API
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Path to your service account credentials JSON file
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'service_account.json')

# Spreadsheet ID (extract from your Google Sheets URL)
SPREADSHEET_ID = os.environ.get('SPREADSHEET_ID', 'your-spreadsheet-id-here')

# Initialize Google Sheets API client
def get_gspread_client():
    """Get an authorized gspread client"""
    try:
        credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return gspread.authorize(credentials)
    except Exception as e:
        print(f"Error initializing gspread client: {e}")
        return None

# Serve Vue frontend
@app.route('/')
def index():
    return app.send_static_file('index.html')

# API Routes
@app.route('/api/members', methods=['GET'])
def get_members():
    try:
        gc = get_gspread_client()
        if not gc:
            return jsonify({"error": "Failed to connect to Google Sheets API"}), 500
            
        # Open the spreadsheet and access the Members worksheet
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        members_sheet = spreadsheet.worksheet("Members")
        
        # Get all records including headers
        all_values = members_sheet.get_all_values()
        
        if len(all_values) <= 1:  # Only headers or empty sheet
            return jsonify([])
        
        # Extract headers from the first row
        headers = all_values[0]
        
        # Convert the remaining rows to a list of dictionaries
        members = []
        for row in all_values[1:]:
            member = {}
            for i, header in enumerate(headers):
                if i < len(row):  # Avoid index out of range
                    member[header] = row[i]
            
            # Add empty string for any missing values
            for header in headers:
                if header not in member:
                    member[header] = ""
                    
            members.append(member)
        
        return jsonify(members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members', methods=['POST'])
def create_member():
    try:
        member_data = request.json
        
        # Generate a unique ID if not provided
        if 'id' not in member_data:
            member_data['id'] = str(uuid.uuid4())
        
        # Set join date to today if not provided
        if 'joinDate' not in member_data or not member_data['joinDate']:
            member_data['joinDate'] = datetime.now().strftime('%Y-%m-%d')
        
        gc = get_gspread_client()
        if not gc:
            return jsonify({"error": "Failed to connect to Google Sheets API"}), 500
            
        # Open the spreadsheet and access the Members worksheet
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        members_sheet = spreadsheet.worksheet("Members")
        
        # Get headers (first row)
        headers = members_sheet.row_values(1)
        
        # Prepare row to insert based on headers
        row_data = []
        for header in headers:
            value = member_data.get(header, "")
            row_data.append(value)
        
        # Append the new member
        members_sheet.append_row(row_data)
        
        return jsonify(member_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/members/recent', methods=['GET'])
def get_recent_members():
    try:
        # Calculate date 24 hours ago
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        gc = get_gspread_client()
        if not gc:
            return jsonify({"error": "Failed to connect to Google Sheets API"}), 500
            
        # Open the spreadsheet and access the Members worksheet
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        members_sheet = spreadsheet.worksheet("Members")
        
        # Get all records including headers
        all_values = members_sheet.get_all_values()
        
        if len(all_values) <= 1:  # Only headers or empty sheet
            return jsonify([])
        
        # Extract headers from the first row
        headers = all_values[0]
        
        # Find the index of the joinDate column
        join_date_index = headers.index('joinDate') if 'joinDate' in headers else -1
        
        # Convert the rows to a list of dictionaries and filter by join date
        recent_members = []
        for row in all_values[1:]:
            member = {}
            for i, header in enumerate(headers):
                if i < len(row):  # Avoid index out of range
                    member[header] = row[i]
            
            # Filter by join date (if column exists)
            if join_date_index >= 0 and join_date_index < len(row):
                join_date = row[join_date_index]
                if join_date >= yesterday:
                    # Add referrer name if applicable
                    if 'referredBy' in member and member['referredBy']:
                        # Find the referrer in all members
                        for m_row in all_values[1:]:
                            if m_row[headers.index('id')] == member['referredBy']:
                                member['referredByName'] = m_row[headers.index('name')]
                                break
                    recent_members.append(member)
        
        return jsonify(recent_members)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/visits', methods=['POST'])
def create_visit():
    try:
        visit_data = request.json
        
        # Generate a unique ID if not provided
        if 'id' not in visit_data:
            visit_data['id'] = str(uuid.uuid4())
        
        # Add timestamp if not provided
        if 'timestamp' not in visit_data:
            visit_data['timestamp'] = datetime.now().isoformat()
        
        gc = get_gspread_client()
        if not gc:
            return jsonify({"error": "Failed to connect to Google Sheets API"}), 500
            
        # Open the spreadsheet and access the Visits worksheet
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        visits_sheet = spreadsheet.worksheet("Visits")
        
        # Get headers (first row)
        headers = visits_sheet.row_values(1)
        
        # Prepare row to insert based on headers
        row_data = []
        for header in headers:
            value = visit_data.get(header, "")
            row_data.append(value)
        
        # Append the new visit
        visits_sheet.append_row(row_data)
        
        # If this is a returning customer visit, add member name
        if visit_data.get('type') == 'returning' and visit_data.get('memberId'):
            # Get member details
            members_sheet = spreadsheet.worksheet("Members")
            try:
                # Find the member with the given ID
                cell = members_sheet.find(visit_data['memberId'])
                if cell:
                    row = members_sheet.row_values(cell.row)
                    headers = members_sheet.row_values(1)
                    name_index = headers.index('name')
                    if name_index < len(row):
                        visit_data['memberName'] = row[name_index]
            except:
                # Member not found, continue without setting name
                pass
        
        return jsonify(visit_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/visits/recent', methods=['GET'])
def get_recent_visits():
    try:
        # Calculate date 24 hours ago
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        gc = get_gspread_client()
        if not gc:
            return jsonify({"error": "Failed to connect to Google Sheets API"}), 500
            
        # Open the spreadsheet and access the Visits and Members worksheets
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        visits_sheet = spreadsheet.worksheet("Visits")
        members_sheet = spreadsheet.worksheet("Members")
        
        # Get all visits records including headers
        visits_values = visits_sheet.get_all_values()
        
        if len(visits_values) <= 1:  # Only headers or empty sheet
            return jsonify([])
        
        # Extract headers from the first row
        visits_headers = visits_values[0]
        
        # Find indexes of relevant columns
        date_index = visits_headers.index('date') if 'date' in visits_headers else -1
        timestamp_index = visits_headers.index('timestamp') if 'timestamp' in visits_headers else -1
        type_index = visits_headers.index('type') if 'type' in visits_headers else -1
        member_id_index = visits_headers.index('memberId') if 'memberId' in visits_headers else -1
        
        # Get all members data for lookup
        members_values = members_sheet.get_all_values()
        members_headers = members_values[0]
        
        # Create a lookup dictionary for member names
        member_lookup = {}
        if len(members_values) > 1:
            id_index = members_headers.index('id') if 'id' in members_headers else -1
            name_index = members_headers.index('name') if 'name' in members_headers else -1
            
            if id_index >= 0 and name_index >= 0:
                for m_row in members_values[1:]:
                    if id_index < len(m_row) and name_index < len(m_row):
                        member_lookup[m_row[id_index]] = m_row[name_index]
        
        # Filter and convert visits to list of dictionaries
        recent_visits = []
        for row in visits_values[1:]:
            visit = {}
            for i, header in enumerate(visits_headers):
                if i < len(row):  # Avoid index out of range
                    visit[header] = row[i]
            
            # Determine visit date from 'date' field or 'timestamp' field
            visit_date = None
            if date_index >= 0 and date_index < len(row) and row[date_index]:
                visit_date = row[date_index]
            elif timestamp_index >= 0 and timestamp_index < len(row) and row[timestamp_index]:
                # Extract date part from timestamp
                try:
                    timestamp = row[timestamp_index]
                    visit_date = timestamp.split('T')[0] if 'T' in timestamp else timestamp
                except:
                    pass
            
            # Filter by date
            if visit_date and visit_date >= yesterday:
                # Add member name for returning customers
                if type_index >= 0 and member_id_index >= 0:
                    if type_index < len(row) and row[type_index] == 'returning':
                        if member_id_index < len(row) and row[member_id_index]:
                            member_id = row[member_id_index]
                            visit['memberName'] = member_lookup.get(member_id, 'Unknown Member')
                
                recent_visits.append(visit)
        
        return jsonify(recent_visits)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/stats', methods=['GET'])
def get_analytics_stats():
    try:
        period = int(request.args.get('period', 30))  # Default to 30 days
        cutoff_date = (datetime.now() - timedelta(days=period)).strftime('%Y-%m-%d')
        
        gc = get_gspread_client()
        if not gc:
            return jsonify({"error": "Failed to connect to Google Sheets API"}), 500
            
        # Open the spreadsheet and access both worksheets
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        members_sheet = spreadsheet.worksheet("Members")
        visits_sheet = spreadsheet.worksheet("Visits")
        
        # Get all members data
        members_values = members_sheet.get_all_values()
        members_headers = members_values[0] if members_values else []
        
        # Get all visits data
        visits_values = visits_sheet.get_all_values()
        visits_headers = visits_values[0] if visits_values else []
        
        # Calculate stats
        total_members = len(members_values) - 1 if members_values else 0  # Subtract header row
        
        # Find new members in the selected period
        new_members = 0
        join_date_index = members_headers.index('joinDate') if 'joinDate' in members_headers else -1
        
        if join_date_index >= 0 and len(members_values) > 1:
            for row in members_values[1:]:  # Skip header row
                if join_date_index < len(row) and row[join_date_index] >= cutoff_date:
                    new_members += 1
        
        # Find visits in the selected period
        period_visits = []
        date_index = visits_headers.index('date') if 'date' in visits_headers else -1
        timestamp_index = visits_headers.index('timestamp') if 'timestamp' in visits_headers else -1
        
        if len(visits_values) > 1:
            for row in visits_values[1:]:  # Skip header row
                visit_date = None
                
                # Try to get date from 'date' field
                if date_index >= 0 and date_index < len(row) and row[date_index]:
                    visit_date = row[date_index]
                # Try to get date from 'timestamp' field if 'date' is not available
                elif timestamp_index >= 0 and timestamp_index < len(row) and row[timestamp_index]:
                    try:
                        timestamp = row[timestamp_index]
                        visit_date = timestamp.split('T')[0] if 'T' in timestamp else timestamp
                    except:
                        pass
                
                if visit_date and visit_date >= cutoff_date:
                    visit = {}
                    for i, header in enumerate(visits_headers):
                        if i < len(row):
                            visit[header] = row[i]
                    period_visits.append(visit)
        
        total_visits = len(period_visits)
        
        # Calculate return rate
        type_index = visits_headers.index('type') if 'type' in visits_headers else -1
        returning_visits = 0
        
        if type_index >= 0:
            for visit in period_visits:
                if visit.get('type') == 'returning':
                    returning_visits += 1
        
        return_rate = round((returning_visits / total_visits * 100) if total_visits > 0 else 0, 1)
        
        stats = {
            "totalMembers": total_members,
            "newMembers": new_members,
            "totalVisits": total_visits,
            "returnRate": return_rate
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/analytics/charts', methods=['GET'])
def get_analytics_charts():
    try:
        period = int(request.args.get('period', 30))  # Default to 30 days
        cutoff_date = (datetime.now() - timedelta(days=period)).strftime('%Y-%m-%d')
        
        gc = get_gspread_client()
        if not gc:
            return jsonify({"error": "Failed to connect to Google Sheets API"}), 500
            
        # Open the spreadsheet and access both worksheets
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        members_sheet = spreadsheet.worksheet("Members")
        visits_sheet = spreadsheet.worksheet("Visits")
        
        # Get all members data
        members_values = members_sheet.get_all_values()
        members_headers = members_values[0] if members_values else []
        
        # Get all visits data
        visits_values = visits_sheet.get_all_values()
        visits_headers = visits_values[0] if visits_values else []
        
        # Find relevant column indexes
        members_join_date_index = members_headers.index('joinDate') if 'joinDate' in members_headers else -1
        visits_date_index = visits_headers.index('date') if 'date' in visits_headers else -1
        visits_timestamp_index = visits_headers.index('timestamp') if 'timestamp' in visits_headers else -1
        visits_type_index = visits_headers.index('type') if 'type' in visits_headers else -1
        visits_channel_index = visits_headers.index('channel') if 'channel' in visits_headers else -1
        visits_other_channel_index = visits_headers.index('otherChannel') if 'otherChannel' in visits_headers else -1
        
        # Filter data for the selected period
        period_members = []
        if members_join_date_index >= 0 and len(members_values) > 1:
            for row in members_values[1:]:  # Skip header row
                if members_join_date_index < len(row) and row[members_join_date_index] >= cutoff_date:
                    member = {}
                    for i, header in enumerate(members_headers):
                        if i < len(row):
                            member[header] = row[i]
                    period_members.append(member)
        
        period_visits = []
        if len(visits_values) > 1:
            for row in visits_values[1:]:  # Skip header row
                visit_date = None
                
                # Try to get date from 'date' field
                if visits_date_index >= 0 and visits_date_index < len(row) and row[visits_date_index]:
                    visit_date = row[visits_date_index]
                # Try to get date from 'timestamp' field if 'date' is not available
                elif visits_timestamp_index >= 0 and visits_timestamp_index < len(row) and row[visits_timestamp_index]:
                    try:
                        timestamp = row[visits_timestamp_index]
                        visit_date = timestamp.split('T')[0] if 'T' in timestamp else timestamp
                    except:
                        pass
                
                if visit_date and visit_date >= cutoff_date:
                    visit = {}
                    for i, header in enumerate(visits_headers):
                        if i < len(row):
                            visit[header] = row[i]
                    period_visits.append(visit)
        
        # Member Growth Chart
        member_growth = {}
        for member in period_members:
            join_date = member.get('joinDate', '')
            if join_date:
                member_growth[join_date] = member_growth.get(join_date, 0) + 1
        
        # Convert to sorted list of date-count pairs
        member_growth_data = [{"date": date, "count": count} for date, count in sorted(member_growth.items())]
        
        # Visit Types Chart
        visit_types = {
            "new": 0,
            "returning": 0
        }
        
        if visits_type_index >= 0:
            for visit in period_visits:
                visit_type = visit.get('type')
                if visit_type in ['new', 'returning']:
                    visit_types[visit_type] += 1
        
        # Referral Sources Chart
        referral_sources = {}
        
        if visits_type_index >= 0 and visits_channel_index >= 0:
            for visit in period_visits:
                if visit.get('type') == 'new':
                    channel = visit.get('channel')
                    if channel == 'other' and 'otherChannel' in visit:
                        channel = visit.get('otherChannel')
                    if channel:
                        referral_sources[channel] = referral_sources.get(channel, 0) + 1
        
        # Visits Time Chart
        visits_time = {}
        
        for visit in period_visits:
            visit_date = visit.get('date')
            if not visit_date and 'timestamp' in visit:
                try:
                    timestamp = visit.get('timestamp')
                    visit_date = timestamp.split('T')[0] if 'T' in timestamp else timestamp
                except:
                    pass
            
            if visit_date:
                visits_time[visit_date] = visits_time.get(visit_date, 0) + 1
        
        # Convert to sorted list of date-count pairs
        visits_time_data = [{"date": date, "count": count} for date, count in sorted(visits_time.items())]
        
        chart_data = {
            "memberGrowth": member_growth_data,
            "visitTypes": visit_types,
            "referralSources": referral_sources,
            "visitsTime": visits_time_data
        }
        
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/export', methods=['GET'])
def export_data():
    try:
        period = int(request.args.get('period', 30))  # Default to 30 days
        cutoff_date = (datetime.now() - timedelta(days=period)).strftime('%Y-%m-%d')
        
        gc = get_gspread_client()
        if not gc:
            return jsonify({"error": "Failed to connect to Google Sheets API"}), 500
            
        # Open the spreadsheet and access both worksheets
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        members_sheet = spreadsheet.worksheet("Members")
        visits_sheet = spreadsheet.worksheet("Visits")
        
        # Get all data including headers
        members_values = members_sheet.get_all_values()
        visits_values = visits_sheet.get_all_values()
        
        if not members_values or not visits_values:
            return jsonify({"error": "No data found in sheets"}), 404
        
        members_headers = members_values[0]
        visits_headers = visits_values[0]
        
        # Find relevant column indexes
        members_join_date_index = members_headers.index('joinDate') if 'joinDate' in members_headers else -1
        visits_date_index = visits_headers.index('date') if 'date' in visits_headers else -1
        visits_timestamp_index = visits_headers.index('timestamp') if 'timestamp' in visits_headers else -1
        visits_type_index = visits_headers.index('type') if 'type' in visits_headers else -1
        visits_member_id_index = visits_headers.index('memberId') if 'memberId' in visits_headers else -1
        
        # Filter data for the selected period
        period_members_data = [members_headers]  # Start with headers
        if members_join_date_index >= 0 and len(members_values) > 1:
            for row in members_values[1:]:  # Skip header row
                if members_join_date_index < len(row) and row[members_join_date_index] >= cutoff_date:
                    period_members_data.append(row)
        
        period_visits_data = [visits_headers]  # Start with headers
        if len(visits_values) > 1:
            for row in visits_values[1:]:  # Skip header row
                visit_date = None
                
                # Try to get date from 'date' field
                if visits_date_index >= 0 and visits_date_index < len(row) and row[visits_date_index]:
                    visit_date = row[visits_date_index]
                # Try to get date from 'timestamp' field if 'date' is not available
                elif visits_timestamp_index >= 0 and visits_timestamp_index < len(row) and row[visits_timestamp_index]:
                    try:
                        timestamp = row[visits_timestamp_index]
                        visit_date = timestamp.split('T')[0] if 'T' in timestamp else timestamp
                    except:
                        pass
                
                if visit_date and visit_date >= cutoff_date:
                    # Add member name for returning visits
                    if (visits_type_index >= 0 and visits_type_index < len(row) and 
                        visits_member_id_index >= 0 and visits_member_id_index < len(row)):
                        if row[visits_type_index] == 'returning' and row[visits_member_id_index]:
                            member_id = row[visits_member_id_index]
                            # Try to find member name
                            found = False
                            for m_row in members_values[1:]:
                                if m_row[members_headers.index('id')] == member_id:
                                    # Add member name to the end of the row if not already present
                                    if 'memberName' not in visits_headers:
                                        if visits_headers[-1] != 'memberName':
                                            visits_headers.append('memberName')
                                            period_visits_data[0] = visits_headers
                                    
                                    # Extend row if needed
                                    member_name_index = visits_headers.index('memberName')
                                    while len(row) <= member_name_index:
                                        row.append("")
                                    
                                    row[member_name_index] = m_row[members_headers.index('name')]
                                    found = True
                                    break
                            
                            if not found and 'memberName' in visits_headers:
                                member_name_index = visits_headers.index('memberName')
                                while len(row) <= member_name_index:
                                    row.append("")
                                row[member_name_index] = "Unknown Member"
                    
                    period_visits_data.append(row)
        
        # Create DataFrames
        members_df = pd.DataFrame(period_members_data[1:], columns=period_members_data[0])
        visits_df = pd.DataFrame(period_visits_data[1:], columns=period_visits_data[0])
        
        # Create summary data
        total_members = len(members_values) - 1  # Exclude header
        new_members = len(period_members_data) - 1  # Exclude header
        total_visits = len(period_visits_data) - 1  # Exclude header
        
        returning_visits = 0
        new_visits = 0
        if visits_type_index >= 0:
            for row in period_visits_data[1:]:  # Skip header
                if visits_type_index < len(row):
                    if row[visits_type_index] == 'returning':
                        returning_visits += 1
                    elif row[visits_type_index] == 'new':
                        new_visits += 1
        
        summary_data = {
            'Metric': ['Total Members', 'New Members', 'Total Visits', 'Returning Visits', 'New Visits'],
            'Value': [total_members, new_members, total_visits, returning_visits, new_visits]
        }
        summary_df = pd.DataFrame(summary_data)
        
        # Create an in-memory Excel file
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            members_df.to_excel(writer, sheet_name='Members', index=False)
            visits_df.to_excel(writer, sheet_name='Visits', index=False)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        output.seek(0)
        
        # Create response
        filename = f"customer_dashboard_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return output.getvalue(), 200, {
            'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'Content-Disposition': f'attachment; filename={filename}'
        }
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Handle errors
@app.errorhandler(404)
def not_found(e):
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)