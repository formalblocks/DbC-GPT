import os
import re
import logging
import pandas as pd
from typing import List, Dict, Any, Optional, Union


class FileUtils:
    """
    Utility class for file operations.
    
    This class provides methods for reading, writing, and processing files.
    """
    
    @staticmethod
    def read_file_content(file_path: str) -> Optional[str]:
        """
        Read the content of a file.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            The content of the file, or None if the file could not be read.
        """
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except IOError as e:
            logging.error(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def save_string_to_file(file_path: str, content: str) -> bool:
        """
        Save a string to a file.
        
        Args:
            file_path: The path to the file.
            content: The content to save.
            
        Returns:
            True if the file was saved successfully, False otherwise.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w') as file:
                file.write(content)
            logging.info(f"Content successfully saved to {file_path}")
            return True
        except IOError as e:
            logging.error(f"Error writing to file {file_path}: {e}")
            return False
    
    @staticmethod
    def save_results_to_csv(file_path: str, results: List[Dict[str, Any]]) -> bool:
        """
        Save results to a CSV file.
        
        Args:
            file_path: The path to the file.
            results: The results to save.
            
        Returns:
            True if the file was saved successfully, False otherwise.
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Convert list of dictionaries to pandas DataFrame
            df = pd.DataFrame(results)
            
            # Save DataFrame to CSV
            df.to_csv(file_path, index=False)
            logging.info(f"Results successfully saved to {file_path}")
            return True
        except Exception as e:
            logging.error(f"Error saving results to CSV {file_path}: {e}")
            return False
    
    @staticmethod
    def extract_content_from_markdown(file_path: str) -> Optional[str]:
        """
        Extract code block or content from a markdown file.
        
        Args:
            file_path: The path to the markdown file.
            
        Returns:
            The extracted content, or None if the file could not be read.
        """
        if file_path == "":
            return ""
            
        content = FileUtils.read_file_content(file_path)
        if content:
            code_match = re.search(r'```solidity\n(.*?)```', content, re.DOTALL)
            if code_match:
                return code_match.group(1)
            return content
        return None
    
    @staticmethod
    def extract_solidity_code(markdown_text: str) -> Optional[str]:
        """
        Extract Solidity code from markdown text.
        
        Args:
            markdown_text: The markdown text.
            
        Returns:
            The extracted Solidity code, or None if no code was found.
        """
        if not markdown_text:
            return None
            
        # Regex pattern to match code blocks with "solidity" as the language identifier
        pattern = r'```solidity\n(.*?)```'
        
        # Use re.DOTALL to match newline characters in the code block
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        
        # Try to return first match
        try:
            return matches[0]
        except IndexError:
            return None
    
    @staticmethod
    def save_thread_to_file(thread_id: str, requested_type: str, context_str: str, 
                         assistant_key: str, run_number: int) -> bool:
        """
        Save thread to a file organized in directories by request type and context.
        
        Args:
            thread_id: The ID of the thread.
            requested_type: The contract type being verified (e.g., "erc20").
            context_str: The context string with underscore separators (e.g., "erc721_erc1155").
            assistant_key: The key for the assistant.
            run_number: The run number.
            
        Returns:
            True if the thread was saved successfully, False otherwise.
        """
        try:
            import openai
            from time import strftime, localtime
            
            # Create directory structure
            combo_dir = f"threads_{assistant_key}/{requested_type}/{context_str}"
            os.makedirs(combo_dir, exist_ok=True)
            
            # Define filename
            filename = f"{combo_dir}/run_{run_number}.txt"
            
            # Retrieve all messages from the thread
            messages = openai.beta.threads.messages.list(
                thread_id=thread_id,
                order="asc"  # Get messages in chronological order
            )
            
            # Open file for writing
            with open(filename, 'w', encoding='utf-8') as file:
                # Write thread ID as header
                file.write(f"Thread ID: {thread_id}\n")
                file.write(f"Request Type: {requested_type}\n")
                file.write(f"Context: {context_str}\n")
                file.write(f"Run: {run_number}\n\n")
                
                # Write each message to the file
                for message in messages.data:
                    role = message.role
                    created_time = strftime('%Y-%m-%d %H:%M:%S', localtime(message.created_at))
                    content = message.content[0].text.value if message.content else "(No content)"
                    
                    file.write(f"=== {role.upper()} [{created_time}] ===\n")
                    file.write(f"{content}\n\n")
                    
                file.write("=== END OF THREAD ===\n")
            
            logging.info(f"Thread saved to {filename}")
            return True
        except Exception as e:
            logging.error(f"Error saving thread to file: {e}")
            return False
            
    @staticmethod
    def load_function_template(requested_type: str, function_name: str) -> Optional[str]:
        """
        Load a function template from a file.
        
        Args:
            requested_type: The contract type (e.g., 'erc20').
            function_name: The name of the function.
            
        Returns:
            The content of the function template file, or None if the file could not be read.
        """
        template_path = f"../assets/file_search/{requested_type.lower()}/{function_name}.md"
        return FileUtils.read_file_content(template_path) 