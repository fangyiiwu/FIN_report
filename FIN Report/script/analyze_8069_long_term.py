import os
import re
import sys
from pypdf import PdfReader

# Flush print to see output immediately
sys.stdout.reconfigure(line_buffering=True)

def parse_page_content(text, keywords, collected_data):
    lines = text.split('\n')
    for line in lines:
        clean_line = line.replace(" ", "")
        for category, key_list in keywords.items():
            match = False
            for key in key_list:
                clean_key = key.replace(" ", "")
                if clean_key in clean_line:
                    match = True
                    break
            
            if match:
                # Basic cleaning to extract numbers
                numbers = re.findall(r'[\d,]+', line)
                if len(numbers) > 0:
                     if category not in collected_data:
                        collected_data[category] = []
                     if line.strip() not in collected_data[category]:
                         collected_data[category].append(line.strip())

def process_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        collected_data = {}
        
        keywords = {
            "Revenue": ["營業收入", "Operating Revenue", "Net Sales"],
            "Gross Profit": ["營業毛利", "Gross Profit"],
            "Operating Income": ["營業利益", "Operating Income"],
            "Net Income": ["本期淨利", "Net Income", "Profit for the year"],
            "EPS": ["基本每股盈餘", "Basic earnings per share"],
            "Cash": ["現金及約當現金", "Cash and cash equivalents"],
            "OCF": ["營業活動之淨現金流入", "Net cash provided by operating activities", "營業活動之淨現金流", "Operating cash flows"],
            "Assets": ["資產總計", "Total Assets"],
            "Liabilities": ["負債總計", "Total Liabilities"],
            "Equity": ["權益總計", "Total Equity", "權益總額"],
            "ROE_Keyword": ["股東權益報酬率", "Return on Equity"]
        }
        
        # Limit to first 300 pages to avoid hanging on appendix
        max_pages = min(len(reader.pages), 300)
        
        for i in range(max_pages):
            try:
                page_text = reader.pages[i].extract_text()
                parse_page_content(page_text, keywords, collected_data)
            except:
                continue # Skip bad pages without failing
                
        return collected_data
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return {}

def main():
    base_dir = r"c:\Users\Philip Wu\Documents\FIN Report\8069"
    output_file = os.path.join(base_dir, "Long_Term_Analysis_8069.md")
    
    # Identify annual reports: 2019-2024
    years = range(2019, 2025)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Long-Term Financial Resilience Analysis - 8069 (2019-2024)\n\n")
        
        for year in years:
            pdf_name = f"8069元太_{year}年報.pdf"
            pdf_path = os.path.join(base_dir, pdf_name)
            
            print(f"Processing {year}...")
            f.write(f"## Year: {year}\n")
            
            if os.path.exists(pdf_path):
                f.write(f"Source: {pdf_name}\n\n")
                data = process_pdf(pdf_path)
                
                if data:
                    for category, lines in data.items():
                        f.write(f"### {category}\n")
                        # Show first 5 matches 
                        for line in lines[:5]: 
                            f.write(f"- {line}\n")
                        f.write("\n")
                else:
                    f.write("No financial data extracted.\n")
            else:
                f.write(f"File not found: {pdf_path}\n")
            
            f.write("---\n\n")
            f.flush() # Force write to disk

    print(f"Long-term analysis complete. Report generated at: {output_file}")

if __name__ == "__main__":
    main()
