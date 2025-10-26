"""
Agent 1: CV Analyzer
Reads a CV (PDF), extracts text, and uses OpenAI to analyze it
"""

import os
import re
import json
from typing import Optional
import PyPDF2
from openai import OpenAI
from dotenv import load_dotenv

from models.models import CVAnalysis

# Load environment variables
load_dotenv()


class CVAnalyzer:
    """
    Agent 1: CV Analyzer

    Analyzes CV/Resume PDFs and extracts structured information:
    - Skills
    - Experience level
    - Years of experience
    - Preferred locations
    - Key achievements
    """

    def __init__(self):
        """Initialize the CV Analyzer with OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")

        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Using mini for cost efficiency

    def _read_pdf(self, cv_path: str) -> str:
        """
        Read text from a PDF file

        Args:
            cv_path: Path to the PDF file

        Returns:
            Extracted text from all pages

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF reading fails
        """
        # Step 1: Check if file exists
        if not os.path.exists(cv_path):
            raise FileNotFoundError(f"CV file not found: {cv_path}")



        with open(cv_path, 'rb') as file:
            # Create PDF reader object
            reader = PyPDF2.PdfReader(file)

            # Initialize empty string to store all text
            text = ""

            # Loop through each page in the PDF
            for page in reader.pages:
                # Extract text from this page and add to total
                text += page.extract_text()

            return text


    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text

        Args:
            text: Raw text from PDF

        Returns:
            Cleaned text
        """
        # Step 1: Replace multiple whitespace characters with single space
        # r'\s+' = regex pattern: \s = any whitespace (space/tab/newline), + = one or more
        text = re.sub(r'\s+', ' ', text)

        # Step 2: Remove leading and trailing whitespace
        text = text.strip()

        return text

    def _create_analysis_prompt(self, cv_text: str) -> list:
        """
        Create the prompt for OpenAI to analyze the CV

        Args:
            cv_text: Cleaned CV text

        Returns:
            List of messages for OpenAI chat API
        """
        system_prompt = """You are an expert CV/Resume analyzer.
Analyze the provided CV and extract structured information.

Return a JSON object with these fields:
{
    "skills": ["skill1", "skill2", ...],
    "experience_level": "Junior" | "Mid" | "Senior" | "Lead",
    "years_of_experience": <number>,
    "preferred_locations": ["location1", "location2", ...],
    "key_achievements": ["achievement1", "achievement2", ...]
}

Guidelines:
- skills: Extract all technical skills, tools, technologies mentioned
- experience_level: Determine based on years and role seniority
- years_of_experience: Total professional experience in years
- preferred_locations: Any locations mentioned or "Remote" if indicated
- key_achievements: Top 3-5 notable achievements or projects

Return ONLY valid JSON, no additional text."""

        user_prompt = f"Analyze this CV:\n\n{cv_text}"

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

    async def analyze(self, cv_path: str) -> CVAnalysis:
        """
        Main method: Analyze a CV and return structured data

        Args:
            cv_path: Path to CV PDF file

        Returns:
            CVAnalysis object with extracted information

        Raises:
            FileNotFoundError: If CV file not found
            Exception: If analysis fails
        """
        print(f"📄 Reading CV from: {cv_path}")

        # Step 1: Read the PDF file
        text = self._read_pdf(cv_path)
        print(f"✅ Read {len(text)} characters from PDF")

        # Step 2: Clean the extracted text
        clean_text = self._clean_text(text)
        print(f"✅ Text cleaned")

        # Step 3: Create the prompt messages for OpenAI
        messages = self._create_analysis_prompt(clean_text)
        print(f"🤖 Calling OpenAI API (this may take 20-60 seconds)...")

        # Step 4: Call OpenAI API to analyze the CV
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"}  # Request JSON response
        )
        print(f"✅ Received response from OpenAI")

        # Step 5: Extract the JSON string from response
        # response.choices[0] = first response option
        # .message.content = the actual content
        result_json = response.choices[0].message.content

        # Step 6: Parse JSON string to Python dictionary
        result_dict = json.loads(result_json)

        # Step 7: Create CVAnalysis object from dictionary
        # ** unpacks the dictionary into named arguments
        cv_analysis = CVAnalysis(**result_dict)

        print(f"✅ Analysis complete!")

        # Step 8: Return the analysis
        return cv_analysis


# Example usage (for testing)
if __name__ == "__main__":
    import asyncio

    async def test():
        analyzer = CVAnalyzer()

        # You'll need to create a sample CV PDF for testing
        cv_path = "/Users/romsheynis/Documents/GitHub/job-finder/cvs/romCV.pdf"

        try:
            result = await analyzer.analyze(cv_path)
            print("\n✅ CV Analysis Result:")
            print(f"Skills: {result.skills}")
            print(f"Experience Level: {result.experience_level}")
            print(f"Years: {result.years_of_experience}")
            print(f"Locations: {result.preferred_locations}")
            print(f"Achievements: {result.key_achievements}")
        except Exception as e:
            print(f"❌ Error: {e}")

    asyncio.run(test())
