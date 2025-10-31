"""
JARVIS AI - File Organization Bot Skill
Automated file sorting, cleanup, and organization.
"""

import os
import shutil
import logging
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from plugins.plugin_manager import PluginBase

class FileOrganizationBot(PluginBase):
    """
    File Organization Bot for automated file management.
    Provides file sorting, duplicate detection, cleanup, and organization.
    """
    
    def __init__(self):
        """Initialize File Organization Bot."""
        super().__init__("FileOrganizationBot", "1.0.0")
        
        # Update metadata
        self.metadata.update({
            'author': 'Jarvis AI Team',
            'description': 'Automated file sorting, cleanup, and organization',
            'category': 'file_management',
            'dependencies': [],
            'compatibility': '1.0.0'
        })
        
        self.logger = logging.getLogger(f"skill.{self.name}")
        
        # File organization settings
        self.organization_rules = {
            'documents': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt'],
            'images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
            'videos': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv'],
            'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
            'archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php'],
            'spreadsheets': ['.xls', '.xlsx', '.csv', '.ods'],
            'presentations': ['.ppt', '.pptx', '.odp']
        }
        
        # Cleanup settings
        self.cleanup_settings = {
            'temp_extensions': ['.tmp', '.temp', '.bak', '.old'],
            'max_file_age_days': 30,
            'min_file_size_mb': 0.1
        }
    
    def initialize(self, config: dict = None) -> bool:
        """Initialize the file organization bot."""
        try:
            self.logger.info(f"Initializing {self.name} skill")
            
            # Load configuration if provided
            if config:
                self.organization_rules.update(config.get('organization_rules', {}))
                self.cleanup_settings.update(config.get('cleanup_settings', {}))
            
            return super().initialize(config)
        except Exception as e:
            self.logger.error(f"Error initializing {self.name} skill: {e}")
            return False
    
    def process_command(self, command: str, context: dict = None) -> dict:
        """Process file organization commands."""
        try:
            command_lower = command.lower()
            
            # File organization
            if any(keyword in command_lower for keyword in ['organize', 'sort', 'arrange', 'files']):
                return self._organize_files(context.get('target_path', '.'))
            
            # Duplicate detection
            elif any(keyword in command_lower for keyword in ['duplicate', 'duplicates', 'find duplicates']):
                return self._find_duplicates(context.get('target_path', '.'))
            
            # File cleanup
            elif any(keyword in command_lower for keyword in ['clean', 'cleanup', 'remove', 'delete']):
                return self._cleanup_files(context.get('target_path', '.'))
            
            # File analysis
            elif any(keyword in command_lower for keyword in ['analyze', 'analysis', 'stats', 'statistics']):
                return self._analyze_files(context.get('target_path', '.'))
            
            # Smart organization
            elif any(keyword in command_lower for keyword in ['smart', 'intelligent', 'auto']):
                return self._smart_organization(context.get('target_path', '.'))
            
            # File structure recommendation
            elif any(keyword in command_lower for keyword in ['structure', 'recommend', 'suggest']):
                return self._recommend_structure(context.get('target_path', '.'))
            
            else:
                return {
                    'success': False,
                    'message': f'{self.name} cannot process: {command}',
                    'data': {},
                    'confidence': 0.0
                }
        
        except Exception as e:
            self.logger.error(f"Error processing command in {self.name}: {e}")
            return {
                'success': False,
                'message': f'Error in {self.name}: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _organize_files(self, target_path: str) -> dict:
        """Organize files by type into appropriate folders."""
        try:
            target_dir = Path(target_path)
            if not target_dir.exists():
                return {
                    'success': False,
                    'message': f'Target path does not exist: {target_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            organized_files = {}
            moved_files = 0
            
            # Create organization folders
            for category in self.organization_rules.keys():
                category_dir = target_dir / category
                category_dir.mkdir(exist_ok=True)
                organized_files[category] = []
            
            # Scan and organize files
            for file_path in target_dir.rglob('*'):
                if file_path.is_file() and file_path.parent != target_dir:
                    file_extension = file_path.suffix.lower()
                    
                    # Find appropriate category
                    for category, extensions in self.organization_rules.items():
                        if file_extension in extensions:
                            # Move file to category folder
                            new_path = target_dir / category / file_path.name
                            
                            # Handle name conflicts
                            counter = 1
                            while new_path.exists():
                                name_parts = file_path.stem, counter, file_path.suffix
                                new_path = target_dir / category / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                                counter += 1
                            
                            try:
                                shutil.move(str(file_path), str(new_path))
                                organized_files[category].append(str(new_path))
                                moved_files += 1
                            except Exception as e:
                                self.logger.warning(f"Could not move {file_path}: {e}")
                            break
            
            return {
                'success': True,
                'message': f'Organized {moved_files} files into {len(self.organization_rules)} categories',
                'data': {
                    'files_moved': moved_files,
                    'categories': organized_files,
                    'target_path': str(target_dir),
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error organizing files: {e}")
            return {
                'success': False,
                'message': f'Error organizing files: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _find_duplicates(self, target_path: str) -> dict:
        """Find duplicate files based on content hash."""
        try:
            target_dir = Path(target_path)
            if not target_dir.exists():
                return {
                    'success': False,
                    'message': f'Target path does not exist: {target_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            file_hashes = {}
            duplicates = []
            
            # Calculate file hashes
            for file_path in target_dir.rglob('*'):
                if file_path.is_file():
                    try:
                        file_hash = self._calculate_file_hash(file_path)
                        if file_hash in file_hashes:
                            duplicates.append({
                                'original': str(file_hashes[file_hash]),
                                'duplicate': str(file_path),
                                'size': file_path.stat().st_size
                            })
                        else:
                            file_hashes[file_hash] = file_path
                    except Exception as e:
                        self.logger.warning(f"Could not hash {file_path}: {e}")
            
            # Calculate total space that could be freed
            total_duplicate_size = sum(dup['size'] for dup in duplicates)
            
            return {
                'success': True,
                'message': f'Found {len(duplicates)} duplicate files',
                'data': {
                    'duplicates': duplicates,
                    'duplicate_count': len(duplicates),
                    'total_size_bytes': total_duplicate_size,
                    'total_size_mb': round(total_duplicate_size / (1024 * 1024), 2),
                    'target_path': str(target_dir),
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error finding duplicates: {e}")
            return {
                'success': False,
                'message': f'Error finding duplicates: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _cleanup_files(self, target_path: str) -> dict:
        """Clean up temporary and old files."""
        try:
            target_dir = Path(target_path)
            if not target_dir.exists():
                return {
                    'success': False,
                    'message': f'Target path does not exist: {target_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            cleaned_files = []
            total_size_freed = 0
            cutoff_date = datetime.now() - timedelta(days=self.cleanup_settings['max_file_age_days'])
            
            # Find files to clean up
            for file_path in target_dir.rglob('*'):
                if file_path.is_file():
                    should_clean = False
                    
                    # Check file extension
                    if file_path.suffix.lower() in self.cleanup_settings['temp_extensions']:
                        should_clean = True
                    
                    # Check file age
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        should_clean = True
                    
                    # Check file size
                    file_size = file_path.stat().st_size
                    if file_size < (self.cleanup_settings['min_file_size_mb'] * 1024 * 1024):
                        should_clean = True
                    
                    if should_clean:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            cleaned_files.append(str(file_path))
                            total_size_freed += file_size
                        except Exception as e:
                            self.logger.warning(f"Could not delete {file_path}: {e}")
            
            return {
                'success': True,
                'message': f'Cleaned up {len(cleaned_files)} files',
                'data': {
                    'files_cleaned': cleaned_files,
                    'files_count': len(cleaned_files),
                    'size_freed_bytes': total_size_freed,
                    'size_freed_mb': round(total_size_freed / (1024 * 1024), 2),
                    'target_path': str(target_dir),
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error cleaning up files: {e}")
            return {
                'success': False,
                'message': f'Error cleaning up files: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _analyze_files(self, target_path: str) -> dict:
        """Analyze file structure and provide statistics."""
        try:
            target_dir = Path(target_path)
            if not target_dir.exists():
                return {
                    'success': False,
                    'message': f'Target path does not exist: {target_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            file_stats = {
                'total_files': 0,
                'total_directories': 0,
                'total_size_bytes': 0,
                'file_types': {},
                'largest_files': [],
                'oldest_files': [],
                'newest_files': []
            }
            
            file_sizes = []
            file_dates = []
            
            # Analyze files
            for file_path in target_dir.rglob('*'):
                if file_path.is_file():
                    file_stats['total_files'] += 1
                    file_size = file_path.stat().st_size
                    file_stats['total_size_bytes'] += file_size
                    file_sizes.append((file_path, file_size))
                    
                    # Track file types
                    file_extension = file_path.suffix.lower()
                    if file_extension:
                        file_stats['file_types'][file_extension] = file_stats['file_types'].get(file_extension, 0) + 1
                    else:
                        file_stats['file_types']['no_extension'] = file_stats['file_types'].get('no_extension', 0) + 1
                    
                    # Track file dates
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    file_dates.append((file_path, file_mtime))
                
                elif file_path.is_dir():
                    file_stats['total_directories'] += 1
            
            # Find largest files
            file_sizes.sort(key=lambda x: x[1], reverse=True)
            file_stats['largest_files'] = [
                {'path': str(f[0]), 'size_bytes': f[1], 'size_mb': round(f[1] / (1024 * 1024), 2)}
                for f in file_sizes[:10]
            ]
            
            # Find oldest and newest files
            file_dates.sort(key=lambda x: x[1])
            file_stats['oldest_files'] = [
                {'path': str(f[0]), 'date': f[1].isoformat()}
                for f in file_dates[:5]
            ]
            
            file_dates.sort(key=lambda x: x[1], reverse=True)
            file_stats['newest_files'] = [
                {'path': str(f[0]), 'date': f[1].isoformat()}
                for f in file_dates[:5]
            ]
            
            return {
                'success': True,
                'message': f'Analyzed {file_stats["total_files"]} files in {file_stats["total_directories"]} directories',
                'data': {
                    **file_stats,
                    'total_size_mb': round(file_stats['total_size_bytes'] / (1024 * 1024), 2),
                    'total_size_gb': round(file_stats['total_size_bytes'] / (1024 * 1024 * 1024), 2),
                    'target_path': str(target_dir),
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.9
            }
        
        except Exception as e:
            self.logger.error(f"Error analyzing files: {e}")
            return {
                'success': False,
                'message': f'Error analyzing files: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _smart_organization(self, target_path: str) -> dict:
        """Intelligent file organization based on content analysis."""
        try:
            target_dir = Path(target_path)
            if not target_dir.exists():
                return {
                    'success': False,
                    'message': f'Target path does not exist: {target_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Analyze current structure
            analysis = self._analyze_files(target_path)
            if not analysis['success']:
                return analysis
            
            # Generate smart organization plan
            organization_plan = self._generate_smart_plan(analysis['data'])
            
            # Execute smart organization
            organized_files = {}
            moved_files = 0
            
            for file_path in target_dir.rglob('*'):
                if file_path.is_file() and file_path.parent != target_dir:
                    # Determine smart category
                    smart_category = self._determine_smart_category(file_path)
                    
                    if smart_category:
                        # Create category folder
                        category_dir = target_dir / smart_category
                        category_dir.mkdir(exist_ok=True)
                        
                        # Move file
                        new_path = category_dir / file_path.name
                        counter = 1
                        while new_path.exists():
                            name_parts = file_path.stem, counter, file_path.suffix
                            new_path = category_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
                            counter += 1
                        
                        try:
                            shutil.move(str(file_path), str(new_path))
                            if smart_category not in organized_files:
                                organized_files[smart_category] = []
                            organized_files[smart_category].append(str(new_path))
                            moved_files += 1
                        except Exception as e:
                            self.logger.warning(f"Could not move {file_path}: {e}")
            
            return {
                'success': True,
                'message': f'Smart organization completed: {moved_files} files organized',
                'data': {
                    'files_moved': moved_files,
                    'organization_plan': organization_plan,
                    'organized_files': organized_files,
                    'target_path': str(target_dir),
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error in smart organization: {e}")
            return {
                'success': False,
                'message': f'Error in smart organization: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _recommend_structure(self, target_path: str) -> dict:
        """Recommend optimal file structure."""
        try:
            target_dir = Path(target_path)
            if not target_dir.exists():
                return {
                    'success': False,
                    'message': f'Target path does not exist: {target_path}',
                    'data': {},
                    'confidence': 0.0
                }
            
            # Analyze current structure
            analysis = self._analyze_files(target_path)
            if not analysis['success']:
                return analysis
            
            # Generate recommendations
            recommendations = self._generate_structure_recommendations(analysis['data'])
            
            return {
                'success': True,
                'message': f'Generated {len(recommendations)} structure recommendations',
                'data': {
                    'recommendations': recommendations,
                    'current_analysis': analysis['data'],
                    'target_path': str(target_dir),
                    'timestamp': datetime.now().isoformat()
                },
                'confidence': 0.8
            }
        
        except Exception as e:
            self.logger.error(f"Error generating structure recommendations: {e}")
            return {
                'success': False,
                'message': f'Error generating recommendations: {e}',
                'data': {},
                'confidence': 0.0
            }
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.logger.warning(f"Could not hash {file_path}: {e}")
            return ""
    
    def _determine_smart_category(self, file_path: Path) -> Optional[str]:
        """Determine smart category for file based on content and context."""
        try:
            # Check file extension first
            file_extension = file_path.suffix.lower()
            for category, extensions in self.organization_rules.items():
                if file_extension in extensions:
                    return category
            
            # Smart categorization based on file name patterns
            file_name = file_path.name.lower()
            
            if any(keyword in file_name for keyword in ['photo', 'image', 'picture', 'pic']):
                return 'images'
            elif any(keyword in file_name for keyword in ['video', 'movie', 'clip']):
                return 'videos'
            elif any(keyword in file_name for keyword in ['music', 'song', 'audio']):
                return 'audio'
            elif any(keyword in file_name for keyword in ['document', 'doc', 'text']):
                return 'documents'
            elif any(keyword in file_name for keyword in ['code', 'script', 'program']):
                return 'code'
            
            # Default to documents for unknown types
            return 'documents'
        
        except Exception as e:
            self.logger.warning(f"Could not determine category for {file_path}: {e}")
            return None
    
    def _generate_smart_plan(self, analysis_data: dict) -> dict:
        """Generate smart organization plan based on analysis."""
        return {
            'total_files': analysis_data['total_files'],
            'suggested_categories': list(self.organization_rules.keys()),
            'optimization_opportunities': [
                'Group similar file types together',
                'Create project-based folders',
                'Archive old files',
                'Remove duplicates'
            ]
        }
    
    def _generate_structure_recommendations(self, analysis_data: dict) -> list:
        """Generate file structure recommendations."""
        recommendations = []
        
        # File type distribution analysis
        file_types = analysis_data.get('file_types', {})
        if file_types:
            most_common = max(file_types.items(), key=lambda x: x[1])
            recommendations.append(f"Most common file type: {most_common[0]} ({most_common[1]} files)")
        
        # Size-based recommendations
        total_size_gb = analysis_data.get('total_size_gb', 0)
        if total_size_gb > 10:
            recommendations.append("Consider archiving large files to save space")
        
        # Organization recommendations
        if analysis_data.get('total_files', 0) > 100:
            recommendations.append("Create subdirectories to organize large file collections")
        
        # Cleanup recommendations
        recommendations.append("Regular cleanup of temporary files recommended")
        recommendations.append("Consider duplicate file removal")
        
        return recommendations
    
    def get_capabilities(self) -> list:
        """Get skill capabilities."""
        return [
            "File organization by type",
            "Duplicate file detection",
            "Temporary file cleanup",
            "File structure analysis",
            "Smart file categorization",
            "Structure recommendations",
            "File statistics and insights",
            "Automated file management"
        ]
