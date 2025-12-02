# HaGOLEM Wiki - Bulk Import Helper
# Use this to import multiple ideas at once from your existing files

import mysql.connector
import json

# ============================================================================
# CONFIGURE YOUR DATABASE
# ============================================================================

DB_CONFIG = {
    'host': 'your-mysql-host.mysql.pythonanywhere-services.com',
    'user': 'your-username',
    'password': 'your-password',
    'database': 'your-database-name'
}

# ============================================================================
# METHOD 1: Import from Python List
# ============================================================================

def import_from_list(ideas_list):
    """
    Import ideas from a Python list.
    Each idea should be a dictionary with these keys:
    - title (required)
    - summary (required)
    - content (required)
    - type (optional)
    - category (optional)
    - priority (optional)
    - tags (optional)
    - source_file (optional)
    """
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    imported = 0
    errors = []
    
    for idea in ideas_list:
        try:
            query = """
                INSERT INTO hagolem_ideas 
                (idea_title, idea_summary, idea_content, idea_type, category, 
                 priority, tags, source_file, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'New')
            """
            values = (
                idea.get('title', 'Untitled'),
                idea.get('summary', ''),
                idea.get('content', ''),
                idea.get('type', 'General'),
                idea.get('category', 'Uncategorized'),
                idea.get('priority', 'Medium'),
                idea.get('tags', ''),
                idea.get('source_file', '')
            )
            
            cursor.execute(query, values)
            imported += 1
            print(f"✓ Imported: {idea.get('title', 'Untitled')}")
        except Exception as e:
            error_msg = f"✗ Error importing '{idea.get('title', 'Unknown')}': {str(e)}"
            errors.append(error_msg)
            print(error_msg)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"IMPORT COMPLETE")
    print(f"{'='*60}")
    print(f"Successfully imported: {imported}")
    print(f"Errors: {len(errors)}")
    if errors:
        print("\nError details:")
        for error in errors:
            print(error)

# ============================================================================
# METHOD 2: Import from JSON File
# ============================================================================

def import_from_json(json_file_path):
    """
    Import ideas from a JSON file.
    
    JSON format should be:
    [
        {
            "title": "Idea Title",
            "summary": "Short summary",
            "content": "Full content here",
            "type": "Business Strategy",
            "category": "Platform",
            "priority": "High",
            "tags": "robot, AI, platform",
            "source_file": "original_file.pptx"
        },
        {
            "title": "Another Idea",
            ...
        }
    ]
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            ideas_list = json.load(f)
        
        print(f"Found {len(ideas_list)} ideas in {json_file_path}")
        import_from_list(ideas_list)
    except Exception as e:
        print(f"Error reading JSON file: {e}")

# ============================================================================
# METHOD 3: Import from CSV File
# ============================================================================

def import_from_csv(csv_file_path):
    """
    Import ideas from a CSV file.
    
    CSV format (first row is header):
    title,summary,content,type,category,priority,tags,source_file
    "Idea 1","Summary 1","Content 1","Business Strategy","Platform","High","tag1, tag2","file.pptx"
    "Idea 2","Summary 2","Content 2","Technical","RoboChef","Medium","tag3","file2.docx"
    """
    import csv
    
    try:
        ideas_list = []
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ideas_list.append({
                    'title': row.get('title', ''),
                    'summary': row.get('summary', ''),
                    'content': row.get('content', ''),
                    'type': row.get('type', 'General'),
                    'category': row.get('category', 'Uncategorized'),
                    'priority': row.get('priority', 'Medium'),
                    'tags': row.get('tags', ''),
                    'source_file': row.get('source_file', '')
                })
        
        print(f"Found {len(ideas_list)} ideas in {csv_file_path}")
        import_from_list(ideas_list)
    except Exception as e:
        print(f"Error reading CSV file: {e}")

# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    print("HaGOLEM Wiki - Bulk Import Tool")
    print("="*60)
    print()
    
    # EXAMPLE 1: Import a list of ideas directly
    # Uncomment and modify this section:
    
    # example_ideas = [
    #     {
    #         'title': 'Created in Our Image - Core Philosophy',
    #         'summary': 'The philosophical foundation of HaGOLEM - humans creating robots in their image, mirroring divine creation.',
    #         'content': '''And humans said: Let us make a GOLEM in our image, body and mind.
    #
    #         PHILOSOPHICAL FRAMEWORK:
    #         This captures the essence of HaGOLEM - completing a circle of creation from Divine to Human to Humanoid.
    #         [... full content here ...]
    #         ''',
    #         'type': 'Business Strategy',
    #         'category': 'Platform',
    #         'priority': 'Critical',
    #         'tags': 'philosophy, core, positioning, GOLEM, creation',
    #         'source_file': 'HaGOLEM_Philosophy_v1.docx'
    #     },
    #     {
    #         'title': 'Platform Economics vs Hardware Competition',
    #         'summary': 'Why HaGOLEM should focus on platform dominance rather than competing with Tesla on hardware.',
    #         'content': 'Detailed analysis of platform vs hardware strategy...',
    #         'type': 'Business Strategy',
    #         'category': 'Platform',
    #         'priority': 'High',
    #         'tags': 'strategy, platform, economics, Tesla, competition',
    #         'source_file': 'Platform_Strategy.pptx'
    #     }
    # ]
    # 
    # import_from_list(example_ideas)
    
    # EXAMPLE 2: Import from JSON file
    # import_from_json('my_ideas.json')
    
    # EXAMPLE 3: Import from CSV file
    # import_from_csv('my_ideas.csv')
    
    print()
    print("Instructions:")
    print("1. Update DB_CONFIG with your database credentials")
    print("2. Uncomment one of the example sections above")
    print("3. Add your ideas")
    print("4. Run this script: python3 import_ideas.py")
    print()

# ============================================================================
# TEMPLATE FOR YOUR IDEAS
# ============================================================================

"""
Copy this template for each idea you want to import:

{
    'title': 'Your Idea Title',
    'summary': 'A 2-3 sentence summary of the idea',
    'content': '''The full detailed content of your idea.
    
    This can be multiple paragraphs.
    Include everything from your original document.
    ''',
    'type': 'Business Strategy',  # or Technical, VC Pitch, Patent, Marketing
    'category': 'Platform',        # or RoboChef, Military, Fundraising, etc.
    'priority': 'High',            # or Critical, Medium, Low
    'tags': 'tag1, tag2, tag3',   # Comma-separated keywords
    'source_file': 'original_file_name.pptx'  # Where this came from
}
"""

# ============================================================================
# QUICK START TEMPLATE - Copy your first 3 ideas here:
# ============================================================================

# STEP 1: Update database credentials above
# STEP 2: Copy this template 3 times
# STEP 3: Fill in your actual ideas
# STEP 4: Uncomment the import_from_list() call
# STEP 5: Run the script

"""
my_first_ideas = [
    {
        'title': '',
        'summary': '',
        'content': '',
        'type': 'Business Strategy',
        'category': 'Platform',
        'priority': 'High',
        'tags': '',
        'source_file': ''
    },
    {
        'title': '',
        'summary': '',
        'content': '',
        'type': '',
        'category': '',
        'priority': 'Medium',
        'tags': '',
        'source_file': ''
    },
    {
        'title': '',
        'summary': '',
        'content': '',
        'type': '',
        'category': '',
        'priority': '',
        'tags': '',
        'source_file': ''
    }
]

# Uncomment this line when ready:
# import_from_list(my_first_ideas)
"""