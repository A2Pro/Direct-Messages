#!/usr/bin/env python3
"""
Consolidate Discord chat CSV exports into a single simplified CSV file.
"""

import pandas as pd
import glob
import os
from datetime import datetime
from tqdm import tqdm

def consolidate_chat_logs():
    # Find all CSV files in the directory
    csv_pattern = "/home/a2/Downloads/Direct Messages/**/*.csv"
    csv_files = glob.glob(csv_pattern, recursive=True)
    
    print(f"Found {len(csv_files)} CSV files to process")
    
    # Initialize list to store simplified data
    consolidated_data = []
    
    # Process each CSV file
    for csv_file in tqdm(csv_files, desc="Processing CSV files"):
        print(f"Processing: {os.path.basename(csv_file)}")
        
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Extract simplified columns
            for _, row in tqdm(df.iterrows(), desc=f"Processing rows in {os.path.basename(csv_file)}", leave=False, total=len(df)):
                simplified_row = {
                    'message_id': row.get('id', ''),
                    'timestamp': row.get('timestamp', ''),
                    'author_username': row.get('author.username', ''),
                    'author_display_name': row.get('author.global_name', ''),
                    'author_id': row.get('author.id', ''),
                    'content': row.get('content', ''),
                    'channel_id': row.get('channel_id', ''),
                    'has_attachments': bool(row.get('attachments', '')),
                    'attachment_url': row.get('attachments.0.url', ''),
                    'attachment_filename': row.get('attachments.0.filename', ''),
                    'message_type': row.get('type', 0),
                    'edited_timestamp': row.get('edited_timestamp', ''),
                    'referenced_message_id': row.get('message_reference.message_id', ''),
                    'source_file': os.path.basename(csv_file)
                }
                
                # Only add if message has content or attachments
                if simplified_row['content'] or simplified_row['has_attachments']:
                    consolidated_data.append(simplified_row)
                    
        except Exception as e:
            print(f"Error processing {csv_file}: {e}")
            continue
    
    # Create DataFrame from consolidated data
    consolidated_df = pd.DataFrame(consolidated_data)
    
    # Sort by timestamp
    consolidated_df = consolidated_df.sort_values('timestamp')
    
    # Save to new CSV file
    output_file = "/home/a2/Downloads/Direct Messages/consolidated_chat.csv"
    consolidated_df.to_csv(output_file, index=False)
    
    print(f"Consolidated {len(consolidated_data)} messages into {output_file}")
    print(f"Total unique authors: {consolidated_df['author_username'].nunique()}")
    print(f"Date range: {consolidated_df['timestamp'].min()} to {consolidated_df['timestamp'].max()}")
    
    return output_file

if __name__ == "__main__":
    consolidate_chat_logs()