from pathlib import Path
import pandas as pd
import pdfplumber
import json

class FileHandler:
    def __init__(self, working_dir: Path):
        self.working_dir = working_dir
    
    def process_file(self, file_path: Path) -> str:
        """Process file and return content"""
        ext = file_path.suffix.lower()
        
        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                content = []
                for page in pdf.pages:
                    if text := page.extract_text():
                        content.append(text)
                    for table in page.extract_tables():
                        if table and len(table) > 1:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            content.append(df.to_markdown(index=False))
                return "\n\n".join(content)
                
        elif ext == ".csv":
            return pd.read_csv(file_path).to_markdown(index=False)
            
        elif ext == ".json":
            return json.dumps(json.loads(file_path.read_text()), indent=2)
            
        elif ext in (".xlsx", ".xls"):
            return pd.read_excel(file_path).to_markdown(index=False)
            
        else:  # txt, md, etc.
            return file_path.read_text(encoding="utf-8")