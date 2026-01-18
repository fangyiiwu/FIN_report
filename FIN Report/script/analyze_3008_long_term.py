import os
import re
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        # Only extract the first 30 pages as financial highlights, consolidated statements usually appear early
        for i, page in enumerate(reader.pages):
            if i > 30: 
                break
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

def parse_long_term_data(text, year):
    # Keywords for Buy & Hold Analysis
    keywords = {
        "Gross Profit": ["營業毛利", "Gross Profit"],
        "Operating Income": ["營業利益", "Operating Income"],
        "Net Income": ["本期淨利", "Net Income"],
        "Cash": ["現金及約當現金", "Cash and cash equivalents"],
        "Assets": ["資產總計", "Total assets"],
        "Liabilities": ["負債總計", "Total liabilities"],
        "Equity": ["權益總計", "Total equity"],
        "OCF": ["營業活動之淨現金流入", "Net cash flows from operating activities"],
        "EPS": ["基本每股盈餘", "Basic earnings per share"],
        "Revenue": ["營業收入", "Net Revenue", "Net Sales"]
    }
    
    found_data = {}
    lines = text.split('\n')
    
    for category, key_list in keywords.items():
        for line in lines:
            for key in key_list:
                if key in line and len(line) < 100: # filter out long narrative lines
                    # Basic cleaning to extract numbers
                    # Look for lines that look like: "營業毛利   10,000,000  50"
                    # We want to capture the large numbers
                    numbers = re.findall(r'[\d,]+', line)
                    # Filter for numbers that look like financial figures (e.g. > 1,000)
                    valid_numbers = [n for n in numbers if len(n.replace(',', '')) > 3]
                    
                    if valid_numbers:
                        if category not in found_data:
                            found_data[category] = []
                        found_data[category].append(f"{line.strip()}")
                        
    return found_data

def main():
    base_dir = r"c:\Users\Philip Wu\Documents\FIN Report\3008"
    output_file = os.path.join(base_dir, "Long_Term_Analysis_3008.md")
    
    # Identify annual reports: 2018-2024
    years = range(2018, 2025)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Long-Term Financial Resilience Analysis - 3008 (2018-2024)\n\n")
        
        for year in years:
            # Match file pattern
            pdf_name = f"3008大立光_{year}年報.pdf"
            pdf_path = os.path.join(base_dir, pdf_name)
            
            f.write(f"## Year: {year}\n")
            if os.path.exists(pdf_path):
                f.write(f"Source: {pdf_name}\n\n")
                text = extract_text_from_pdf(pdf_path)
                
                # DEBUG: Write raw text start to file to check content
                if year == 2023:
                    print(f"DEBUG: Raw text for 2023 (first 500 chars):\n{text[:500]}")
                
                data = parse_long_term_data(text, year)
                
                if data:
                    for category, lines in data.items():
                        f.write(f"### {category}\n")
                        # Show first 3 matches to avoid clutter, usually the first one is the consolidation table
                        for line in lines[:3]: 
                            f.write(f"- {line}\n")
                        f.write("\n")
                else:
                    f.write("No financial data extracted. File might be image-based or protected.\n")
            else:
                f.write(f"File not found: {pdf_path}\n")
            
            f.write("---\n\n")

    print(f"Long-term analysis complete. Report generated at: {output_file}")

if __name__ == "__main__":
    main()
