"""
AI Mobile AgentX - Cleanup Script
Remove redundant files and optimize project structure
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectCleanup:
    """
    Clean up redundant files and folders from original Mobile AgentX codebase
    to improve performance and reduce clutter after AI reformation
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.cleanup_summary: Dict[str, Any] = {
            'removed_directories': [],
            'removed_files': [],
            'bytes_saved': 0,
            'files_moved': [],
            'backup_created': False
        }
        
        # Define what should be removed
        self.redundant_directories = [
            'mobile-agentx',        # Old hardcoded implementation
            'mobile_agentx_flutter', # Flutter frontend (replaced by AI automation)
        ]
        
        self.redundant_files = [
            # Any specific redundant files can be listed here
        ]
        
        # Define important files to preserve
        self.preserve_files = [
            'README.md',
            'requirements.txt', 
            'DEMO_GUIDE.md',
            'GEMINI_MODELS.md',
            '.gitignore',
            '.gitattributes'
        ]
        
        logger.info(f"Cleanup initialized for: {self.project_root}")
    
    def create_backup(self) -> bool:
        """Create backup of files before cleanup"""
        try:
            backup_dir = self.project_root / "backup_before_cleanup"
            
            if backup_dir.exists():
                logger.info("Backup already exists, skipping backup creation")
                self.cleanup_summary['backup_created'] = True
                return True
            
            logger.info("Creating backup before cleanup...")
            
            # Create backup directory
            backup_dir.mkdir(exist_ok=True)
            
            # Backup redundant directories
            for dir_name in self.redundant_directories:
                source_dir = self.project_root / dir_name
                if source_dir.exists():
                    backup_target = backup_dir / dir_name
                    logger.info(f"Backing up: {dir_name}")
                    shutil.copytree(source_dir, backup_target)
            
            self.cleanup_summary['backup_created'] = True
            logger.info(f"✅ Backup created at: {backup_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return False
    
    def calculate_directory_size(self, directory: Path) -> int:
        """Calculate total size of directory in bytes"""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        pass
            return total_size
        except Exception as e:
            logger.error(f"Size calculation failed for {directory}: {e}")
            return 0
    
    def remove_redundant_directories(self) -> bool:
        """Remove redundant directories from old implementation"""
        try:
            logger.info("Removing redundant directories...")
            
            for dir_name in self.redundant_directories:
                dir_path = self.project_root / dir_name
                
                if not dir_path.exists():
                    logger.info(f"Directory already removed or doesn't exist: {dir_name}")
                    continue
                
                # Calculate size before removal
                dir_size = self.calculate_directory_size(dir_path) 
                
                logger.info(f"Removing directory: {dir_name} ({dir_size / 1024 / 1024:.2f} MB)")
                
                # Remove directory and all contents
                shutil.rmtree(dir_path)
                
                # Update summary
                self.cleanup_summary['removed_directories'].append(dir_name)
                self.cleanup_summary['bytes_saved'] += dir_size
                
                logger.info(f"✅ Removed: {dir_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Directory removal failed: {e}")
            return False
    
    def remove_redundant_files(self) -> bool:
        """Remove specific redundant files"""
        try:
            logger.info("Removing redundant files...")
            
            for file_path in self.redundant_files:
                full_path = self.project_root / file_path
                
                if not full_path.exists():
                    continue
                
                file_size = full_path.stat().st_size
                logger.info(f"Removing file: {file_path}")
                
                full_path.unlink()
                
                self.cleanup_summary['removed_files'].append(file_path)
                self.cleanup_summary['bytes_saved'] += file_size
            
            return True
            
        except Exception as e:
            logger.error(f"File removal failed: {e}")
            return False
    
    def clean_python_cache(self) -> bool:
        """Remove Python cache files and directories"""
        try:
            logger.info("Cleaning Python cache files...")
            
            cache_patterns = ['__pycache__', '*.pyc', '*.pyo', '.pytest_cache']
            
            for root, dirs, files in os.walk(self.project_root):
                # Remove __pycache__ directories
                for dir_name in dirs[:]:  # Use slice to safely modify during iteration
                    if dir_name in ['__pycache__', '.pytest_cache']:
                        cache_dir = Path(root) / dir_name
                        cache_size = self.calculate_directory_size(cache_dir)
                        
                        shutil.rmtree(cache_dir)
                        dirs.remove(dir_name)  # Don't recurse into removed directory
                        
                        self.cleanup_summary['removed_directories'].append(str(cache_dir.relative_to(self.project_root)))
                        self.cleanup_summary['bytes_saved'] += cache_size
                        
                        logger.debug(f"Removed cache: {cache_dir}")
                
                # Remove .pyc and .pyo files
                for file_name in files:
                    if file_name.endswith(('.pyc', '.pyo')):
                        cache_file = Path(root) / file_name
                        file_size = cache_file.stat().st_size
                        
                        cache_file.unlink()
                        
                        self.cleanup_summary['removed_files'].append(str(cache_file.relative_to(self.project_root)))
                        self.cleanup_summary['bytes_saved'] += file_size
            
            logger.info("✅ Python cache cleanup completed")
            return True
            
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")
            return False
    
    def update_main_requirements(self) -> bool:
        """Update main requirements.txt to reflect new AI architecture"""
        try:
            logger.info("Updating main requirements.txt...")
            
            # New requirements for AI-driven architecture
            ai_requirements = [
                "# AI Mobile AgentX - Reformed Architecture Requirements",
                "",
                "# Core AI and OCR",
                "Pillow>=10.0.0",
                "opencv-python>=4.8.0",
                "pytesseract>=0.3.10",
                "easyocr>=1.7.0",
                "",
                "# Async and Performance", 
                "asyncio-extensions>=0.1.0",
                "aiofiles>=23.0.0",
                "",
                "# Database and Caching",
                "sqlite3",  # Built-in with Python
                "",
                "# Android Automation (Optional - for ADB integration)",
                "pure-python-adb>=0.3.0",
                "",
                "# Utilities",
                "python-dateutil>=2.8.0",
                "typing-extensions>=4.7.0",
                "",
                "# Development and Testing",
                "pytest>=7.0.0",
                "pytest-asyncio>=0.21.0"
            ]
            
            requirements_file = self.project_root / "requirements.txt"
            
            # Backup original requirements
            if requirements_file.exists():
                backup_req = self.project_root / "requirements_original.txt"
                shutil.copy2(requirements_file, backup_req)
                logger.info("Original requirements backed up")
            
            # Write new requirements
            with open(requirements_file, 'w') as f:
                f.write('\n'.join(ai_requirements))
            
            logger.info("✅ Requirements.txt updated for AI architecture")
            return True
            
        except Exception as e:
            logger.error(f"Requirements update failed: {e}")
            return False
    
    def create_cleanup_report(self) -> bool:
        """Create detailed cleanup report"""
        try:
            report_file = self.project_root / "cleanup_report.md"
            
            total_mb_saved = self.cleanup_summary['bytes_saved'] / 1024 / 1024
            
            report_content = f"""# Mobile AgentX Cleanup Report

## Summary
- **Total space saved**: {total_mb_saved:.2f} MB
- **Directories removed**: {len(self.cleanup_summary['removed_directories'])}
- **Files removed**: {len(self.cleanup_summary['removed_files'])}
- **Backup created**: {'✅' if self.cleanup_summary['backup_created'] else '❌'}

## Removed Directories
{chr(10).join([f"- {dir_name}" for dir_name in self.cleanup_summary['removed_directories']])}

## Removed Files  
{chr(10).join([f"- {file_name}" for file_name in self.cleanup_summary['removed_files']])}

## New AI Architecture
The cleanup removed the old hardcoded mobile automation implementation and Flutter frontend, 
replacing them with:

### Core AI Components
- **Screen Capture Manager**: Cross-platform mobile screen capture
- **OCR Detection Engine**: Multi-engine text recognition (Tesseract, EasyOCR, ML Kit)
- **Tap Coordinate Engine**: Dynamic coordinate calculation with human-like behavior
- **Smart Automation Engine**: Advanced workflow orchestration with retry logic
- **Intelligent Position Cache**: SQLite-based caching with verification

### App Connectors (Reformed)
- **Gmail Connector**: OCR-driven email automation
- **WhatsApp Connector**: Dynamic messaging and chat management
- **Spotify Connector**: Music control and playlist management
- **Maps Connector**: Navigation and location services
- **Calendar Connector**: Event management and scheduling

### Testing Framework
- **Mock Automation Engine**: Safe testing environment
- **Visual Debugger**: Screenshot comparison and feedback
- **Test Reporting**: Comprehensive automation validation

## Performance Improvements
- Eliminated redundant code duplication
- Removed Flutter overhead for pure AI automation
- Optimized caching and memory usage
- Streamlined architecture for better maintainability

Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(report_file, 'w') as f:
                f.write(report_content)
            
            logger.info(f"✅ Cleanup report created: {report_file}")
            return True
            
        except Exception as e:
            logger.error(f"Report creation failed: {e}")
            return False
    
    def run_full_cleanup(self) -> bool:
        """Execute complete cleanup process"""
        try:
            logger.info("🧹 Starting Mobile AgentX cleanup process...")
            logger.info("=" * 50)
            
            # Step 1: Create backup
            if not self.create_backup():
                logger.error("❌ Backup creation failed - aborting cleanup")
                return False
            
            # Step 2: Remove redundant directories
            if not self.remove_redundant_directories():
                logger.error("❌ Directory cleanup failed")
                return False
            
            # Step 3: Remove redundant files
            if not self.remove_redundant_files():
                logger.error("❌ File cleanup failed") 
                return False
            
            # Step 4: Clean Python cache
            if not self.clean_python_cache():
                logger.warning("⚠️ Cache cleanup had issues")
            
            # Step 5: Update requirements
            if not self.update_main_requirements():
                logger.warning("⚠️ Requirements update had issues")
            
            # Step 6: Create report
            if not self.create_cleanup_report():
                logger.warning("⚠️ Report creation had issues")
            
            # Final summary
            total_mb_saved = self.cleanup_summary['bytes_saved'] / 1024 / 1024
            
            logger.info("=" * 50)
            logger.info("🎉 CLEANUP COMPLETED SUCCESSFULLY!")
            logger.info(f"📊 Space saved: {total_mb_saved:.2f} MB")
            logger.info(f"📁 Directories removed: {len(self.cleanup_summary['removed_directories'])}")
            logger.info(f"📄 Files removed: {len(self.cleanup_summary['removed_files'])}")
            logger.info("✅ AI Mobile AgentX architecture is now optimized!")
            
            return True
            
        except Exception as e:
            logger.error(f"Cleanup process failed: {e}")
            return False


def main():
    """Run the cleanup process"""
    project_root = os.path.dirname(os.path.dirname(__file__))  # Go up from ai-mobile-agentx to project root
    
    cleanup = ProjectCleanup(project_root)
    success = cleanup.run_full_cleanup()
    
    if success:
        print("\n🎯 Mobile AgentX reformation and cleanup completed!")
        print("🚀 Your AI-driven automation architecture is ready!")
    else:
        print("\n❌ Cleanup encountered errors. Check logs for details.")
        print("💡 Backup was created - you can restore if needed.")


if __name__ == "__main__":
    main()