#!/usr/bin/env python3
"""
Data Analysis Script for Member Messages
Analyzes the dataset for anomalies, inconsistencies, and patterns
"""
import httpx
import asyncio
import json
from collections import Counter, defaultdict
from datetime import datetime
import re

# Correct URL with trailing slash
MEMBER_API_URL = "https://november7-730026606190.europe-west1.run.app/messages"

class DataAnalyzer:
    def __init__(self, data):
        self.data = data
        self.items = data.get("items", [])
        self.total = data.get("total", 0)
        self.findings = []
        
    def analyze_all(self):
        """Run all analysis checks"""
        print("=" * 80)
        print("DATA ANALYSIS REPORT")
        print("=" * 80)
        print(f"\nTotal messages: {self.total}")
        print(f"Messages retrieved: {len(self.items)}")
        print("\n")
        
        self.check_schema_consistency()
        self.check_data_types()
        self.check_user_names()
        self.check_timestamps()
        self.check_message_content()
        self.check_duplicates()
        self.extract_insights()
        
        self.print_summary()
    
    def check_schema_consistency(self):
        """Check if all items have consistent schema"""
        print("1. Schema Consistency Check")
        print("-" * 80)
        
        expected_fields = {"id", "user_id", "user_name", "timestamp", "message"}
        schemas = [set(item.keys()) for item in self.items]
        
        unique_schemas = set(tuple(sorted(s)) for s in schemas)
        
        if len(unique_schemas) == 1:
            print("✓ All messages have consistent schema")
            schema = list(unique_schemas)[0]
            print(f"  Fields: {', '.join(schema)}")
        else:
            print("✗ Inconsistent schemas detected!")
            for schema in unique_schemas:
                count = sum(1 for s in schemas if tuple(sorted(s)) == schema)
                print(f"  Schema variant ({count} messages): {', '.join(schema)}")
            self.findings.append("Inconsistent schemas across messages")
        
        # Check for missing fields
        missing_fields = []
        for item in self.items:
            for field in expected_fields:
                if field not in item or item[field] is None or item[field] == "":
                    missing_fields.append((item.get("id", "unknown"), field))
        
        if missing_fields:
            print(f"\n✗ Found {len(missing_fields)} missing/empty fields")
            for msg_id, field in missing_fields[:5]:
                print(f"  Message {msg_id}: missing '{field}'")
            if len(missing_fields) > 5:
                print(f"  ... and {len(missing_fields) - 5} more")
            self.findings.append(f"{len(missing_fields)} missing/empty fields")
        else:
            print("\n✓ No missing or empty fields detected")
        
        print()
    
    def check_data_types(self):
        """Check data type consistency"""
        print("2. Data Type Consistency Check")
        print("-" * 80)
        
        field_types = defaultdict(set)
        for item in self.items:
            for key, value in item.items():
                field_types[key].add(type(value).__name__)
        
        inconsistent = False
        for field, types in field_types.items():
            if len(types) > 1:
                print(f"✗ Field '{field}' has multiple types: {', '.join(types)}")
                inconsistent = True
                self.findings.append(f"Field '{field}' has inconsistent types")
        
        if not inconsistent:
            print("✓ All fields have consistent data types")
        
        print()
    
    def check_user_names(self):
        """Check for user name inconsistencies"""
        print("3. User Name Analysis")
        print("-" * 80)
        
        user_names = [item.get("user_name") for item in self.items if item.get("user_name")]
        user_ids = [item.get("user_id") for item in self.items if item.get("user_id")]
        
        unique_names = set(user_names)
        unique_ids = set(user_ids)
        
        print(f"Unique user names: {len(unique_names)}")
        print(f"Unique user IDs: {len(unique_ids)}")
        
        # List all unique users
        print(f"\nAll members:")
        for name in sorted(unique_names):
            count = user_names.count(name)
            print(f"  - {name}: {count} message(s)")
        
        name_patterns = defaultdict(list)
        for name in unique_names:
            first_name = name.split()[0] if name else ""
            name_patterns[first_name.lower()].append(name)
        
        potential_duplicates = {k: v for k, v in name_patterns.items() if len(v) > 1}
        if potential_duplicates:
            print(f"\n✗ Potential name variations detected:")
            for base_name, variations in list(potential_duplicates.items())[:5]:
                print(f"  {base_name}: {', '.join(variations)}")
            self.findings.append(f"{len(potential_duplicates)} potential name variations")
        else:
            print("\n✓ No obvious name variations detected")
        
        user_mapping = defaultdict(set)
        for item in self.items:
            user_id = item.get("user_id")
            user_name = item.get("user_name")
            if user_id and user_name:
                user_mapping[user_id].add(user_name)
        
        inconsistent_mappings = {k: v for k, v in user_mapping.items() if len(v) > 1}
        if inconsistent_mappings:
            print(f"\n✗ User IDs with multiple names:")
            for user_id, names in list(inconsistent_mappings.items())[:3]:
                print(f"  User {user_id}: {', '.join(names)}")
            self.findings.append(f"{len(inconsistent_mappings)} user IDs with multiple names")
        
        print()
    
    def check_timestamps(self):
        """Check timestamp format and validity"""
        print("4. Timestamp Analysis")
        print("-" * 80)
        
        timestamps = [item.get("timestamp") for item in self.items if item.get("timestamp")]
        
        parsed_dates = []
        parse_errors = []
        
        for ts in timestamps:
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                parsed_dates.append(dt)
            except:
                parse_errors.append(ts)
        
        if parse_errors:
            print(f"✗ Failed to parse {len(parse_errors)} timestamps")
            for ts in parse_errors[:3]:
                print(f"  {ts}")
            self.findings.append(f"{len(parse_errors)} unparseable timestamps")
        else:
            print(f"✓ All {len(timestamps)} timestamps parsed successfully")
        
        if parsed_dates:
            earliest = min(parsed_dates)
            latest = max(parsed_dates)
            print(f"\nDate range:")
            print(f"  Earliest: {earliest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Latest: {latest.strftime('%Y-%m-%d %H:%M:%S')}")
            
            now = datetime.now(parsed_dates[0].tzinfo)
            future_dates = [d for d in parsed_dates if d > now]
            if future_dates:
                print(f"\n✗ Found {len(future_dates)} messages with future timestamps")
                self.findings.append(f"{len(future_dates)} future timestamps")
            else:
                print(f"\n✓ No future timestamps detected")
        
        print()
    
    def check_message_content(self):
        """Analyze message content"""
        print("5. Message Content Analysis")
        print("-" * 80)
        
        messages = [item.get("message", "") for item in self.items]
        
        lengths = [len(msg) for msg in messages]
        avg_length = sum(lengths) / len(lengths) if lengths else 0
        
        print(f"Total messages: {len(messages)}")
        print(f"Average message length: {avg_length:.1f} characters")
        print(f"Shortest message: {min(lengths) if lengths else 0} characters")
        print(f"Longest message: {max(lengths) if lengths else 0} characters")
        
        empty_messages = sum(1 for msg in messages if not msg or msg.strip() == "")
        if empty_messages:
            print(f"\n✗ Found {empty_messages} empty messages")
            self.findings.append(f"{empty_messages} empty messages")
        else:
            print(f"\n✓ No empty messages detected")
        
        print("\nContent pattern analysis:")
        
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
            r'\b\d{1,2}/\d{1,2}/\d{4}\b'
        ]
        
        messages_with_dates = sum(1 for msg in messages 
                                  if any(re.search(pattern, msg, re.IGNORECASE) 
                                       for pattern in date_patterns))
        print(f"  Messages with dates: {messages_with_dates} ({messages_with_dates/len(messages)*100:.1f}%)")
        
        messages_with_numbers = sum(1 for msg in messages if re.search(r'\b\d+\b', msg))
        print(f"  Messages with numbers: {messages_with_numbers} ({messages_with_numbers/len(messages)*100:.1f}%)")
        
        # Topic detection
        travel_keywords = ['trip', 'travel', 'flight', 'hotel', 'vacation', 'visit', 'booking']
        food_keywords = ['restaurant', 'dinner', 'lunch', 'reservation', 'table', 'chef', 'menu']
        event_keywords = ['ticket', 'concert', 'show', 'performance', 'event', 'seats']
        
        travel_msgs = sum(1 for msg in messages if any(kw in msg.lower() for kw in travel_keywords))
        food_msgs = sum(1 for msg in messages if any(kw in msg.lower() for kw in food_keywords))
        event_msgs = sum(1 for msg in messages if any(kw in msg.lower() for kw in event_keywords))
        
        print(f"\nTopic distribution:")
        print(f"  Travel-related: {travel_msgs} messages ({travel_msgs/len(messages)*100:.1f}%)")
        print(f"  Food/Dining: {food_msgs} messages ({food_msgs/len(messages)*100:.1f}%)")
        print(f"  Events/Entertainment: {event_msgs} messages ({event_msgs/len(messages)*100:.1f}%)")
        
        print()
    
    def check_duplicates(self):
        """Check for duplicate messages"""
        print("6. Duplicate Detection")
        print("-" * 80)
        
        ids = [item.get("id") for item in self.items if item.get("id")]
        id_counts = Counter(ids)
        duplicate_ids = {k: v for k, v in id_counts.items() if v > 1}
        
        if duplicate_ids:
            print(f"✗ Found {len(duplicate_ids)} duplicate message IDs")
            for msg_id, count in list(duplicate_ids.items())[:3]:
                print(f"  ID {msg_id}: appears {count} times")
            self.findings.append(f"{len(duplicate_ids)} duplicate message IDs")
        else:
            print("✓ No duplicate message IDs found")
        
        messages = [item.get("message") for item in self.items if item.get("message")]
        message_counts = Counter(messages)
        duplicate_messages = {k: v for k, v in message_counts.items() if v > 1}
        
        if duplicate_messages:
            print(f"\n✗ Found {len(duplicate_messages)} duplicate messages")
            for msg, count in list(duplicate_messages.items())[:3]:
                preview = msg[:50] + "..." if len(msg) > 50 else msg
                print(f"  '{preview}': appears {count} times")
            self.findings.append(f"{len(duplicate_messages)} duplicate message contents")
        else:
            print("\n✓ No duplicate message content found")
        
        print()
    
    def extract_insights(self):
        """Extract interesting insights from the data"""
        print("7. Data Insights & Member Activity")
        print("-" * 80)
        
        user_counts = Counter(item.get("user_name") for item in self.items if item.get("user_name"))
        print(f"\nMember activity (sorted by message count):")
        for user, count in user_counts.most_common():
            print(f"  {user}: {count} message(s)")
        
        print()
    
    def print_summary(self):
        """Print summary of findings"""
        print("=" * 80)
        print("SUMMARY OF FINDINGS")
        print("=" * 80)
        
        if self.findings:
            print(f"\nIdentified {len(self.findings)} data quality observations:")
            for i, finding in enumerate(self.findings, 1):
                print(f"  {i}. {finding}")
        else:
            print("\n✓ No data quality issues detected!")
            print("  - All schemas are consistent")
            print("  - All data types are uniform")
            print("  - No duplicate IDs or messages")
            print("  - All timestamps are valid")
            print("  - No empty messages")
        
        print("\n" + "=" * 80)

async def fetch_and_analyze():
    """Fetch data and run analysis"""
    print("Fetching data from API...")
    print(f"URL: {MEMBER_API_URL}\n")
    
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(MEMBER_API_URL)
            response.raise_for_status()
            data = response.json()
            
            print(f"✓ Successfully fetched data")
            print(f"  Status code: {response.status_code}")
            print(f"  Total messages in API: {data.get('total', 0)}")
            print(f"  Messages in this response: {len(data.get('items', []))}\n")
            
            if not data.get("items"):
                print("⚠️ Warning: No messages found in the response")
                return
            
            analyzer = DataAnalyzer(data)
            analyzer.analyze_all()
            
            # Save results
            result_data = {
                "total_messages": data.get("total", 0),
                "messages_analyzed": len(data.get("items", [])),
                "unique_members": len(set(item.get("user_name") for item in data.get("items", []) if item.get("user_name"))),
                "findings": analyzer.findings,
                "member_list": sorted(set(item.get("user_name") for item in data.get("items", []) if item.get("user_name"))),
                "timestamp": datetime.now().isoformat(),
                "analysis_status": "completed"
            }
            
            with open("data_analysis_results.json", "w") as f:
                json.dump(result_data, f, indent=2)
            
            print("\n✓ Analysis results saved to data_analysis_results.json")
            
        except httpx.HTTPStatusError as e:
            print(f"✗ HTTP Error: {e.response.status_code}")
            print(f"  URL: {e.request.url}")
            print(f"  Response: {e.response.text[:200]}")
        except Exception as e:
            print(f"✗ Error fetching data: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(fetch_and_analyze())
