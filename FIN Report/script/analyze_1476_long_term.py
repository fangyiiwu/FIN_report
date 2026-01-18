import os
import re
import sys
from pypdf import PdfReader

# Flush print to see output immediately
sys.stdout.reconfigure(line_buffering=True)

def check_text_extractability(reader, check_pages=20):
    """Check if the PDF has sufficient text content in the first few pages."""
    total_valid_chars = 0
    pages_to_check = min(len(reader.pages), check_pages)
    
    for i in range(pages_to_check):
        try:
            text = reader.pages[i].extract_text()
            if text:
                # Remove whitespace and check density
                total_valid_chars += len(text.strip())
        except:
            pass
            
    # Threshold: Average 50 chars per page is extremely low for an annual report
    if total_valid_chars < 500:
        return False, total_valid_chars
    return True, total_valid_chars

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

def process_pdf(pdf_path, year, results_summary):
    try:
        reader = PdfReader(pdf_path)
        
        # 1. Check if file is image-based
        is_extractable, char_count = check_text_extractability(reader)
        if not is_extractable:
            msg = f"Skipping {year}: Low text content (Chars: {char_count}). Likely Image/Image-Scan."
            print(msg)
            results_summary["skipped"].append(year)
            return None, msg

        # 2. Extract Data
        collected_data = {}
        keywords = {
            "Revenue": ["營業收入", "Operating Revenue", "Net Sales", "合約客戶收入"],
            "Gross Profit": ["營業毛利", "Gross Profit"],
            "Operating Income": ["營業利益", "Operating Income"],
            "Net Income": ["本期淨利", "Net Income", "Profit for the year", "本期損益"],
            "EPS": ["基本每股盈餘", "Basic earnings per share"],
            "Cash": ["現金及約當現金", "Cash and cash equivalents"],
            "OCF": ["營業活動之淨現金流入", "Net cash provided by operating activities", "營業活動之淨現金流", "Operating cash flows"],
            "Assets": ["資產總計", "Total Assets", "資產總額"],
            "Liabilities": ["負債總計", "Total Liabilities", "負債總額"],
            "Equity": ["權益總計", "Total Equity", "權益總額"],
            "ROE_Keyword": ["股東權益報酬率", "Return on Equity"]
        }
        
        # Limit to first 300 pages to avoid hanging on appendix
        max_pages = min(len(reader.pages), 350)
        
        for i in range(max_pages):
            try:
                page_text = reader.pages[i].extract_text()
                if page_text:
                    # DEBUG: Print snippet of 2023 page 10 to see structure
                    if year == 2023 and i == 10:
                        print(f"DEBUG 2023 Page 10 snippet:\n{page_text[:500]}")
                    parse_page_content(page_text, keywords, collected_data)
            except:
                continue 
        
        if not collected_data:
             msg = "No keywords matched with numbers."
             return None, msg

        results_summary["processed"].append(year)
        return collected_data, "Success"
        
    except Exception as e:
        msg = f"Error processing {pdf_path}: {e}"
        print(msg)
        results_summary["error"].append(year)
        return None, msg

def main():
    base_dir = r"c:\Users\Philip Wu\Documents\FIN Report\1476"
    output_file = os.path.join(base_dir, "Long_Term_Analysis_1476.md")
    
    # Identify annual reports: 2019-2024 (Based on file listing)
    years = range(2019, 2025)
    
    results_summary = {"processed": [], "skipped": [], "error": []}
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Long-Term Financial Resilience Analysis - 1476 (2019-2024)\n\n")
        
        for year in years:
            pdf_name = f"{year}_1476_年報.pdf"
            pdf_path = os.path.join(base_dir, pdf_name)
            
            print(f"Checking {year}...")
            f.write(f"## Year: {year}\n")
            
            if os.path.exists(pdf_path):
                f.write(f"Source: {pdf_name}\n\n")
                data, status_msg = process_pdf(pdf_path, year, results_summary)
                
                if data:
                    for category, lines in data.items():
                        f.write(f"### {category}\n")
                        # Show first 5 matches 
                        for line in lines[:5]: 
                            f.write(f"- {line}\n")
                        f.write("\n")
                else:
                    f.write(f"**Extraction Failed/Skipped:** {status_msg}\n")
            else:
                f.write(f"File not found: {pdf_path}\n")
            
            f.write("---\n\n")
            f.flush()

    # Final check on success rate
    total_files = len(years)
    skipped_count = len(results_summary["skipped"]) + len(results_summary["error"])
    
    print("\n--- Summary ---")
    print(f"Processed: {len(results_summary['processed'])}")
    print(f"Skipped/Error: {skipped_count}")
    
    print(f"Analysis complete. Report generated at: {output_file}")

if __name__ == "__main__":
    main()
