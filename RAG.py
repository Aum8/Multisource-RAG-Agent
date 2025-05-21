import dspy
from pathlib import Path
from typing import Dict
import json
import re
import os

class RAGProcessor:
    def __init__(self, working_dir: Path):
        self.working_dir = working_dir
        self.lm = dspy.LM(model='gemini/gemini-1.5-flash', api_key=os.getenv("GOOGLE_API_KEY"))
        dspy.settings.configure(lm=self.lm)
        
        # Define DSPy signatures
        self.select_files = dspy.Predict("question, file_info -> relevant_files")
        self.answer_question = dspy.Predict("question, context -> answer")
        self.summarize_content = dspy.Predict("content -> summary")

    def extract_headers(self, content: str) -> list:
        """
        Extract headers from the content. Assumes headers follow common patterns like:
        - Markdown headers (e.g., # Header, ## Subheader)
        - Titles in uppercase or surrounded by newlines
        """
        # Regex to match common header patterns
        header_patterns = [
            r"^# .+",
            r"^## .+",
            r"^[A-Z][A-Z0-9\s\-]+$",
            r"^\s*\n.+\n\s*$"
        ]
        headers = []
        for pattern in header_patterns:
            headers.extend(re.findall(pattern, content, re.MULTILINE))
        return headers

    def summarize_with_headers(self, content: str) -> str:
        """
        Summarize content based on headers. If no headers are found, summarize the entire content.
        """
        headers = self.extract_headers(content)
        if headers:
            # Extract sections under each header
            sections = []
            for i, header in enumerate(headers):
                # Find the content under the header until the next header
                start_idx = content.find(header)
                end_idx = content.find(headers[i + 1], start_idx) if i + 1 < len(headers) else len(content)
                sections.append(content[start_idx:end_idx])
            
            # Summarize each section and combine
            summarized_sections = [
                self.summarize_content(content=section[:1000]).summary
                for section in sections
            ]
            return "\n\n".join(summarized_sections)
        else:
            # Fallback to summarizing the entire content
            return self.summarize_content(content = content[:3000]).summary

    def generate_description_with_summary(self, file_name: str, content: str) -> str:
        """
        Generate a description for the file. If no description is provided, summarize the content.
        """
        # Summarize content using headers if available
        summary = self.summarize_with_headers(content)
        return f"{file_name}: {summary}"

    def select_relevant_files(self, question: str, sources: Dict) -> list:
        """Select only relevant files for the question"""
        if not sources:
            return []

        # Prepare file info for DSPy
        file_info = [
            {
                "name": info["name"],
                "description": info["description"]
            }
            for info in sources.values()
        ]

        result = self.select_files(
            question=question,
            file_info=json.dumps(file_info, indent=2)
        )
        
        # Print DSPy result
        print("DSPy result:", result)
        
        try:
            # Parse relevant files
            relevant_files = [f.strip() for f in result.relevant_files.split(",") if f.strip()]
            print("Parsed relevant files:", relevant_files)
            return relevant_files
        except Exception as e:
            print("Error parsing relevant files:", e)
            return list(sources.keys())  # Fallback to all files if selection fails

    def query(self, question: str, sources: Dict) -> str:
        """Generate answer using only relevant sources"""
        if not sources:
            raise ValueError("No files provided. Please provide files to analyze.")

        # Generate descriptions for files that don't have them
        for file_path, info in sources.items():
            if not info.get("description"):
                info["description"] = self.generate_description_with_summary(
                    file_name=info["name"],
                    content=info["content"]
                )
                sources[file_path] = info

        # Map file names to file paths
        file_name_to_path = {info["name"]: file_path for file_path, info in sources.items()}

        # Select relevant files
        relevant_files = self.select_relevant_files(question, sources)

        # Map relevant file names to paths
        relevant_file_paths = [
            file_name_to_path[file] for file in relevant_files if file in file_name_to_path
        ]

        if not relevant_file_paths:
            raise ValueError("No relevant files found. Please check your input.")

        # Prepare context from selected sources
        context = "\n\n".join(
            f"From {sources[file]['name']} ({sources[file]['description']}):\n{sources[file]['content'][:1000]}"
            for file in relevant_file_paths
        )

        result = self.answer_question(
            question=question,
            context=context
        )
        total_tokens_used = sum(entry.get('usage', {}).get('total_tokens', 0) for entry in self.lm.history)
        print(f"Total tokens used: {total_tokens_used}")
        return result.answer