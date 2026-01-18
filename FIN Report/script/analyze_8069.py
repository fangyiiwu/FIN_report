import os
import re
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading {pdf_path}: {e}"

def parse_financial_data(text):
    data = {}
    lines = text.split('\n')
    extracted_lines = []
    
    keywords = [
        "Net Sales", "Gross Profit", "Operating Income", "Net Income", "Earnings Per Share", "Revenue", "EPS",
        "營業收入", "營業毛利", "營業利益", "本期淨利", "基本每股盈餘", "稀釋每股盈餘", "綜合損益",
        "Research and Development", "R&D", "研究發展費用", "研發費用"
    ]
    
    for line in lines:
        for keyword in keywords:
            if keyword.lower() in line.lower():
                extracted_lines.append(line.strip())
                
    return extracted_lines

def main():
    base_dir = r"c:\Users\Philip Wu\Documents\FIN Report\8069"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(base_dir, "Analysis_8069_2025_FullYear.md")
    
    pdf_files = [
        "202501_8069_AI1_20260118_025345.pdf",
        "202502_8069_AI1_20260118_025347.pdf",
        "202503_8069_AI1_20260118_025348.pdf",
        "8069法說會.pdf"
    ]
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Financial Analysis for E Ink (8069) - 2025 Full Year\n\n")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(base_dir, pdf_file)
            f.write(f"## Report: {pdf_file}\n\n")
            
            if os.path.exists(pdf_path):
                text = extract_text_from_pdf(pdf_path)
                
                f.write("### Key Financial Figures Detected:\n")
                extracted_data = parse_financial_data(text)
                if extracted_data:
                    for line in extracted_data:
                        f.write(f"- {line}\n")
                else:
                    f.write("- No specific keywords found. Raw text preview (first 500 chars):\n")
                    f.write(f"> {text[:500]}...\n")
                
                f.write("\n---\n\n")
            else:
                f.write(f"**Error:** File not found: {pdf_path}\n\n")

    print(f"Analysis complete. Report generated at: {output_file}")

if __name__ == "__main__":
    main()
