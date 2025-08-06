#!/usr/bin/env python3
"""
Document Update Script - Python Version
Description: Replace content surrounded by specific comments in all md files with corresponding file content
Universal format: <!-- filename --> content <!-- /filename -->
The script will automatically detect all comment tags in this format and replace them with the corresponding file content
"""

import os
import re
import tempfile
import shutil
import glob
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import json
import random
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class APIKeyConfig:
    """Configuration for API keys management"""
    openai_keys: List[str]
    anthropic_keys: List[str] 
    google_keys: List[str]
    current_openai_index: int = 0
    current_anthropic_index: int = 0
    current_google_index: int = 0

class MultiAPIManager:
    """Manages multiple API keys with rotation and fallback"""
    
    def __init__(self, config_file: str = "api_config.json"):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> APIKeyConfig:
        """Load API configuration from file or environment"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return APIKeyConfig(**data)
        
        # Fallback to environment variables
        return APIKeyConfig(
            openai_keys=self._get_env_keys("OPENAI_API_KEY"),
            anthropic_keys=self._get_env_keys("ANTHROPIC_API_KEY"),
            google_keys=self._get_env_keys("GOOGLE_API_KEY")
        )
    
    def _get_env_keys(self, base_key: str) -> List[str]:
        """Get API keys from environment variables"""
        keys = []
        # Try base key
        if os.getenv(base_key):
            keys.append(os.getenv(base_key))
        
        # Try numbered keys
        i = 1
        while True:
            key = os.getenv(f"{base_key}_{i}")
            if key:
                keys.append(key)
                i += 1
            else:
                break
        
        return keys
    
    def get_next_key(self, provider: str) -> Optional[str]:
        """Get next API key for the specified provider with rotation"""
        if provider.lower() == "openai" and self.config.openai_keys:
            key = self.config.openai_keys[self.config.current_openai_index]
            self.config.current_openai_index = (self.config.current_openai_index + 1) % len(self.config.openai_keys)
            return key
        elif provider.lower() == "anthropic" and self.config.anthropic_keys:
            key = self.config.anthropic_keys[self.config.current_anthropic_index]
            self.config.current_anthropic_index = (self.config.current_anthropic_index + 1) % len(self.config.anthropic_keys)
            return key
        elif provider.lower() == "google" and self.config.google_keys:
            key = self.config.google_keys[self.config.current_google_index]
            self.config.current_google_index = (self.config.current_google_index + 1) % len(self.config.google_keys)
            return key
        
        return None
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config.__dict__, f, indent=2)

class DocumentUpdater:
    """Main class for document updating functionality"""
    
    def __init__(self):
        self.api_manager = MultiAPIManager()
        
        # File sync configuration
        self.files_to_sync = [
            "docker-compose-example.yml:yaml",
            ".env.example:env",
            # Add more files as needed
        ]
        
        # Excluded directories
        self.excluded_dirs = {'.venv', '.git', 'node_modules', '__pycache__', '.pytest_cache'}
    
    def get_filename(self, entry: str) -> str:
        """Extract filename from config entry"""
        return entry.split(':')[0] if ':' in entry else entry
    
    def get_configured_code_type(self, entry: str) -> str:
        """Extract code type from config entry"""
        return entry.split(':')[1] if ':' in entry else ""
    
    def get_code_type(self, filename: str) -> str:
        """Infer code type based on file extension"""
        extension = Path(filename).suffix.lower().lstrip('.')
        
        type_mapping = {
            'yml': 'yaml', 'yaml': 'yaml',
            'json': 'json',
            'js': 'javascript', 'mjs': 'javascript',
            'ts': 'typescript',
            'py': 'python',
            'sh': 'bash', 'bash': 'bash',
            'css': 'css',
            'html': 'html', 'htm': 'html',
            'xml': 'xml',
            'sql': 'sql',
            'md': 'markdown',
            'txt': 'text', 'log': 'text', 'conf': 'text', 'config': 'text',
            'env': 'env', 'example': 'env',
            'dockerfile': 'dockerfile',
            'nginx': 'nginx',
        }
        
        return type_mapping.get(extension, 'text')
    
    def check_file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        if not os.path.isfile(file_path):
            logger.warning(f"Warning: {file_path} does not exist, skipping")
            return False
        return True
    
    def process_file(self, md_file: str, source_file: str, start_tag: str, end_tag: str, code_type: str) -> bool:
        """Process file replacement"""
        logger.info(f"Processing file: {md_file} (replacing with {source_file} content)")
        
        try:
            # Read source file content
            with open(source_file, 'r', encoding='utf-8') as f:
                source_content = f.read()
            
            # Read markdown file
            with open(md_file, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Create regex pattern for replacement
            pattern = re.compile(
                rf'({re.escape(start_tag)}).*?({re.escape(end_tag)})',
                re.DOTALL
            )
            
            # Replace content
            replacement = f"{start_tag}\n```{code_type}\n{source_content}\n```\n{end_tag}"
            new_content = pattern.sub(replacement, md_content)
            
            # Write back to file
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Updated: {md_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing {md_file}: {str(e)}")
            return False
    
    def find_markdown_files(self) -> List[str]:
        """Find all markdown files excluding specified directories"""
        md_files = []
        
        for root, dirs, files in os.walk('.'):
            # Remove excluded directories from the search
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
        
        return md_files
    
    def display_file_status(self):
        """Display configured file list status"""
        logger.info("Configured file list:")
        for entry in self.files_to_sync:
            filename = self.get_filename(entry)
            code_type = self.get_configured_code_type(entry)
            
            if os.path.isfile(filename):
                logger.info(f"  ✓ {filename} ({code_type})")
            else:
                logger.info(f"  ✗ {filename} ({code_type}) - file not found")
    
    def update_documents(self):
        """Main function to update all documents"""
        logger.info("Starting document update process...")
        logger.info("")
        
        # Display configured file list
        self.display_file_status()
        
        logger.info("")
        logger.info("Starting file replacement process...")
        
        # Find all markdown files
        md_files = self.find_markdown_files()
        
        for md_file in md_files:
            logger.info(f"Checking file: {md_file}")
            file_updated = False
            
            # Check configured file list
            for entry in self.files_to_sync:
                source_file = self.get_filename(entry)
                
                # Create tag patterns
                start_tag = f"<!-- {source_file} -->"
                end_tag = f"<!-- /{source_file} -->"
                
                # Check if tags exist in markdown file
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    if start_tag in content and end_tag in content:
                        # Check if source file exists
                        if self.check_file_exists(source_file):
                            # Get code type
                            code_type = self.get_configured_code_type(entry)
                            if not code_type:
                                code_type = self.get_code_type(source_file)
                            
                            # Process file
                            if self.process_file(md_file, source_file, start_tag, end_tag, code_type):
                                file_updated = True
                                
                except Exception as e:
                    logger.error(f"Error reading {md_file}: {str(e)}")
                    continue
            
            if not file_updated:
                logger.info(f"Skipping file: {md_file} (no configured file reference tags found)")
        
        logger.info("")
        logger.info("Script execution completed!")
        self.print_usage_instructions()
    
    def print_usage_instructions(self):
        """Print usage instructions"""
        logger.info("")
        logger.info("Usage Instructions:")
        logger.info("1. Add files to sync in the files_to_sync list")
        logger.info("2. Use format in markdown files: <!-- filename --> ... <!-- /filename -->")
        logger.info("3. Run the script to automatically sync content")
        logger.info("")
        logger.info("Supported code types:")
        logger.info("  yaml, json, javascript, typescript, python, bash, css, html, xml, sql, markdown, env, dockerfile, nginx, text")
        logger.info("")
        logger.info("Ignored directories:")
        logger.info("  .venv, .git, node_modules, __pycache__, .pytest_cache")

def main():
    """Main entry point"""
    updater = DocumentUpdater()
    updater.update_documents()

if __name__ == "__main__":
    main()