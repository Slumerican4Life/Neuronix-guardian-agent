"""
Development Tools Integration for Lyra
=====================================

Comprehensive integration module for development tools including VS Code, GitHub, and development workflows.
Provides unified interface for code management, repository operations, and development automation.
"""

import os
import json
import subprocess
import requests
import base64
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging
from pathlib import Path

class DevelopmentToolsIntegration:
    """Unified development tools integration for Lyra"""
    
    def __init__(self, github_token: str = None, vscode_path: str = None):
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.vscode_path = vscode_path or self._find_vscode_path()
        
        # GitHub API configuration
        self.github_api_base = "https://api.github.com"
        self.github_headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Lyra-AI-System"
        }
        
        if self.github_token:
            self.github_headers["Authorization"] = f"token {self.github_token}"
        
        # VS Code configuration
        self.vscode_extensions_path = None
        self.active_workspace = None
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("lyra.dev_tools")
        
        # Initialize components
        self._initialize_components()
    
    def _find_vscode_path(self) -> Optional[str]:
        """Find VS Code installation path"""
        possible_paths = [
            "/usr/bin/code",
            "/usr/local/bin/code",
            "/snap/bin/code",
            "/opt/visual-studio-code/bin/code",
            "code"  # If in PATH
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"Found VS Code at: {path}")
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        
        print("VS Code not found in standard locations")
        return None
    
    def _initialize_components(self):
        """Initialize development tools components"""
        try:
            # Test GitHub API access
            if self.github_token:
                response = requests.get(f"{self.github_api_base}/user", headers=self.github_headers)
                if response.status_code == 200:
                    user_data = response.json()
                    self.logger.info(f"GitHub API authenticated as: {user_data.get('login')}")
                else:
                    self.logger.warning("GitHub API authentication failed")
            else:
                self.logger.warning("No GitHub token provided - some features will be limited")
            
            # Test VS Code access
            if self.vscode_path:
                self.logger.info("VS Code integration available")
            else:
                self.logger.warning("VS Code not available - some features will be limited")
                
        except Exception as e:
            self.logger.error(f"Error initializing development tools: {e}")
    
    # ==================== GITHUB OPERATIONS ====================
    
    def get_user_repositories(self, username: str = None, repo_type: str = "all") -> List[Dict]:
        """Get user repositories"""
        try:
            if username:
                url = f"{self.github_api_base}/users/{username}/repos"
            else:
                url = f"{self.github_api_base}/user/repos"
            
            params = {
                "type": repo_type,  # all, owner, member
                "sort": "updated",
                "per_page": 100
            }
            
            response = requests.get(url, headers=self.github_headers, params=params)
            response.raise_for_status()
            
            repos = response.json()
            
            formatted_repos = []
            for repo in repos:
                formatted_repos.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo.get('description', ''),
                    'private': repo['private'],
                    'html_url': repo['html_url'],
                    'clone_url': repo['clone_url'],
                    'ssh_url': repo['ssh_url'],
                    'language': repo.get('language'),
                    'size': repo['size'],
                    'stargazers_count': repo['stargazers_count'],
                    'forks_count': repo['forks_count'],
                    'created_at': repo['created_at'],
                    'updated_at': repo['updated_at'],
                    'pushed_at': repo['pushed_at']
                })
            
            self.logger.info(f"Retrieved {len(formatted_repos)} repositories")
            return formatted_repos
            
        except requests.RequestException as e:
            self.logger.error(f"Error getting repositories: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error processing repositories: {e}")
            return []
    
    def create_repository(self, name: str, description: str = "", private: bool = False,
                         auto_init: bool = True, gitignore_template: str = None,
                         license_template: str = None) -> Optional[Dict]:
        """Create a new GitHub repository"""
        try:
            data = {
                "name": name,
                "description": description,
                "private": private,
                "auto_init": auto_init
            }
            
            if gitignore_template:
                data["gitignore_template"] = gitignore_template
            
            if license_template:
                data["license_template"] = license_template
            
            response = requests.post(f"{self.github_api_base}/user/repos", 
                                   headers=self.github_headers, json=data)
            response.raise_for_status()
            
            repo_data = response.json()
            
            self.logger.info(f"Created repository: {repo_data['full_name']}")
            return {
                'id': repo_data['id'],
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'html_url': repo_data['html_url'],
                'clone_url': repo_data['clone_url'],
                'ssh_url': repo_data['ssh_url']
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error creating repository: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing repository creation: {e}")
            return None
    
    def get_repository_contents(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """Get repository contents"""
        try:
            url = f"{self.github_api_base}/repos/{owner}/{repo}/contents/{path}"
            
            response = requests.get(url, headers=self.github_headers)
            response.raise_for_status()
            
            contents = response.json()
            
            # Handle single file vs directory
            if isinstance(contents, dict):
                contents = [contents]
            
            formatted_contents = []
            for item in contents:
                formatted_contents.append({
                    'name': item['name'],
                    'path': item['path'],
                    'type': item['type'],  # file or dir
                    'size': item.get('size', 0),
                    'sha': item['sha'],
                    'download_url': item.get('download_url'),
                    'html_url': item['html_url']
                })
            
            self.logger.info(f"Retrieved {len(formatted_contents)} items from {owner}/{repo}/{path}")
            return formatted_contents
            
        except requests.RequestException as e:
            self.logger.error(f"Error getting repository contents: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error processing repository contents: {e}")
            return []
    
    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get file content from repository"""
        try:
            url = f"{self.github_api_base}/repos/{owner}/{repo}/contents/{path}"
            
            response = requests.get(url, headers=self.github_headers)
            response.raise_for_status()
            
            file_data = response.json()
            
            if file_data['type'] != 'file':
                self.logger.error(f"Path {path} is not a file")
                return None
            
            # Decode base64 content
            content = base64.b64decode(file_data['content']).decode('utf-8')
            
            self.logger.info(f"Retrieved file content: {owner}/{repo}/{path}")
            return content
            
        except requests.RequestException as e:
            self.logger.error(f"Error getting file content: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing file content: {e}")
            return None
    
    def create_or_update_file(self, owner: str, repo: str, path: str, content: str,
                             message: str, branch: str = "main", sha: str = None) -> Optional[Dict]:
        """Create or update file in repository"""
        try:
            url = f"{self.github_api_base}/repos/{owner}/{repo}/contents/{path}"
            
            # Encode content to base64
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            data = {
                "message": message,
                "content": encoded_content,
                "branch": branch
            }
            
            # If updating existing file, include SHA
            if sha:
                data["sha"] = sha
            
            response = requests.put(url, headers=self.github_headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            action = "Updated" if sha else "Created"
            self.logger.info(f"{action} file: {owner}/{repo}/{path}")
            
            return {
                'sha': result['content']['sha'],
                'html_url': result['content']['html_url'],
                'download_url': result['content']['download_url']
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error creating/updating file: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing file operation: {e}")
            return None
    
    def create_issue(self, owner: str, repo: str, title: str, body: str = "",
                    labels: List[str] = None, assignees: List[str] = None) -> Optional[Dict]:
        """Create issue in repository"""
        try:
            url = f"{self.github_api_base}/repos/{owner}/{repo}/issues"
            
            data = {
                "title": title,
                "body": body
            }
            
            if labels:
                data["labels"] = labels
            
            if assignees:
                data["assignees"] = assignees
            
            response = requests.post(url, headers=self.github_headers, json=data)
            response.raise_for_status()
            
            issue_data = response.json()
            
            self.logger.info(f"Created issue: {owner}/{repo}#{issue_data['number']}")
            
            return {
                'id': issue_data['id'],
                'number': issue_data['number'],
                'title': issue_data['title'],
                'html_url': issue_data['html_url'],
                'state': issue_data['state']
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error creating issue: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing issue creation: {e}")
            return None
    
    def get_repository_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """Get repository issues"""
        try:
            url = f"{self.github_api_base}/repos/{owner}/{repo}/issues"
            
            params = {
                "state": state,  # open, closed, all
                "per_page": 100
            }
            
            response = requests.get(url, headers=self.github_headers, params=params)
            response.raise_for_status()
            
            issues = response.json()
            
            formatted_issues = []
            for issue in issues:
                # Skip pull requests (they appear in issues API)
                if 'pull_request' in issue:
                    continue
                
                formatted_issues.append({
                    'id': issue['id'],
                    'number': issue['number'],
                    'title': issue['title'],
                    'body': issue.get('body', ''),
                    'state': issue['state'],
                    'html_url': issue['html_url'],
                    'created_at': issue['created_at'],
                    'updated_at': issue['updated_at'],
                    'labels': [label['name'] for label in issue.get('labels', [])],
                    'assignees': [assignee['login'] for assignee in issue.get('assignees', [])]
                })
            
            self.logger.info(f"Retrieved {len(formatted_issues)} issues from {owner}/{repo}")
            return formatted_issues
            
        except requests.RequestException as e:
            self.logger.error(f"Error getting issues: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error processing issues: {e}")
            return []
    
    def create_pull_request(self, owner: str, repo: str, title: str, head: str, base: str,
                           body: str = "", draft: bool = False) -> Optional[Dict]:
        """Create pull request"""
        try:
            url = f"{self.github_api_base}/repos/{owner}/{repo}/pulls"
            
            data = {
                "title": title,
                "head": head,
                "base": base,
                "body": body,
                "draft": draft
            }
            
            response = requests.post(url, headers=self.github_headers, json=data)
            response.raise_for_status()
            
            pr_data = response.json()
            
            self.logger.info(f"Created pull request: {owner}/{repo}#{pr_data['number']}")
            
            return {
                'id': pr_data['id'],
                'number': pr_data['number'],
                'title': pr_data['title'],
                'html_url': pr_data['html_url'],
                'state': pr_data['state']
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error creating pull request: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing pull request creation: {e}")
            return None
    
    # ==================== VS CODE OPERATIONS ====================
    
    def open_vscode(self, path: str = None, new_window: bool = False) -> bool:
        """Open VS Code with optional path"""
        try:
            if not self.vscode_path:
                self.logger.error("VS Code not available")
                return False
            
            cmd = [self.vscode_path]
            
            if new_window:
                cmd.append("--new-window")
            
            if path:
                cmd.append(path)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Opened VS Code: {path or 'default'}")
                return True
            else:
                self.logger.error(f"Failed to open VS Code: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error opening VS Code: {e}")
            return False
    
    def install_vscode_extension(self, extension_id: str) -> bool:
        """Install VS Code extension"""
        try:
            if not self.vscode_path:
                self.logger.error("VS Code not available")
                return False
            
            cmd = [self.vscode_path, "--install-extension", extension_id]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Installed VS Code extension: {extension_id}")
                return True
            else:
                self.logger.error(f"Failed to install extension: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing VS Code extension: {e}")
            return False
    
    def list_vscode_extensions(self) -> List[str]:
        """List installed VS Code extensions"""
        try:
            if not self.vscode_path:
                self.logger.error("VS Code not available")
                return []
            
            cmd = [self.vscode_path, "--list-extensions"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                extensions = result.stdout.strip().split('\n')
                extensions = [ext for ext in extensions if ext]  # Remove empty lines
                
                self.logger.info(f"Found {len(extensions)} VS Code extensions")
                return extensions
            else:
                self.logger.error(f"Failed to list extensions: {result.stderr}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error listing VS Code extensions: {e}")
            return []
    
    def create_vscode_workspace(self, workspace_path: str, folders: List[str],
                               settings: Dict = None, extensions: Dict = None) -> bool:
        """Create VS Code workspace file"""
        try:
            workspace_config = {
                "folders": [{"path": folder} for folder in folders]
            }
            
            if settings:
                workspace_config["settings"] = settings
            
            if extensions:
                workspace_config["extensions"] = extensions
            
            with open(workspace_path, 'w') as f:
                json.dump(workspace_config, f, indent=2)
            
            self.logger.info(f"Created VS Code workspace: {workspace_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating VS Code workspace: {e}")
            return False
    
    # ==================== GIT OPERATIONS ====================
    
    def clone_repository(self, repo_url: str, local_path: str, branch: str = None) -> bool:
        """Clone Git repository"""
        try:
            cmd = ["git", "clone"]
            
            if branch:
                cmd.extend(["-b", branch])
            
            cmd.extend([repo_url, local_path])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Cloned repository: {repo_url} to {local_path}")
                return True
            else:
                self.logger.error(f"Failed to clone repository: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error cloning repository: {e}")
            return False
    
    def git_commit_and_push(self, repo_path: str, message: str, files: List[str] = None,
                           branch: str = None, push: bool = True) -> bool:
        """Commit and push changes to Git repository"""
        try:
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            try:
                # Add files
                if files:
                    for file in files:
                        subprocess.run(["git", "add", file], check=True)
                else:
                    subprocess.run(["git", "add", "."], check=True)
                
                # Commit
                subprocess.run(["git", "commit", "-m", message], check=True)
                
                # Push if requested
                if push:
                    push_cmd = ["git", "push"]
                    if branch:
                        push_cmd.extend(["origin", branch])
                    
                    subprocess.run(push_cmd, check=True)
                
                self.logger.info(f"Committed and pushed changes: {message}")
                return True
                
            finally:
                os.chdir(original_dir)
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Git operation failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error in git commit/push: {e}")
            return False
    
    def create_git_branch(self, repo_path: str, branch_name: str, checkout: bool = True) -> bool:
        """Create Git branch"""
        try:
            original_dir = os.getcwd()
            os.chdir(repo_path)
            
            try:
                # Create branch
                subprocess.run(["git", "branch", branch_name], check=True)
                
                # Checkout if requested
                if checkout:
                    subprocess.run(["git", "checkout", branch_name], check=True)
                
                self.logger.info(f"Created Git branch: {branch_name}")
                return True
                
            finally:
                os.chdir(original_dir)
                
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to create Git branch: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error creating Git branch: {e}")
            return False
    
    # ==================== PROJECT MANAGEMENT ====================
    
    def create_project_structure(self, project_path: str, project_type: str = "python") -> bool:
        """Create standard project structure"""
        try:
            project_path = Path(project_path)
            project_path.mkdir(parents=True, exist_ok=True)
            
            if project_type == "python":
                # Python project structure
                (project_path / "src").mkdir(exist_ok=True)
                (project_path / "tests").mkdir(exist_ok=True)
                (project_path / "docs").mkdir(exist_ok=True)
                (project_path / "scripts").mkdir(exist_ok=True)
                
                # Create files
                (project_path / "README.md").touch()
                (project_path / "requirements.txt").touch()
                (project_path / "setup.py").touch()
                (project_path / ".gitignore").write_text(self._get_python_gitignore())
                
            elif project_type == "javascript":
                # JavaScript/Node.js project structure
                (project_path / "src").mkdir(exist_ok=True)
                (project_path / "test").mkdir(exist_ok=True)
                (project_path / "docs").mkdir(exist_ok=True)
                (project_path / "public").mkdir(exist_ok=True)
                
                # Create files
                (project_path / "README.md").touch()
                (project_path / "package.json").touch()
                (project_path / ".gitignore").write_text(self._get_javascript_gitignore())
                
            elif project_type == "web":
                # Web project structure
                (project_path / "src").mkdir(exist_ok=True)
                (project_path / "assets").mkdir(exist_ok=True)
                (project_path / "css").mkdir(exist_ok=True)
                (project_path / "js").mkdir(exist_ok=True)
                (project_path / "images").mkdir(exist_ok=True)
                
                # Create files
                (project_path / "index.html").touch()
                (project_path / "README.md").touch()
                (project_path / ".gitignore").write_text(self._get_web_gitignore())
            
            self.logger.info(f"Created {project_type} project structure: {project_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating project structure: {e}")
            return False
    
    def _get_python_gitignore(self) -> str:
        """Get Python .gitignore template"""
        return """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# celery beat schedule file
celerybeat-schedule

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json
"""
    
    def _get_javascript_gitignore(self) -> str:
        """Get JavaScript .gitignore template"""
        return """# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# Directory for instrumented libs generated by jscoverage/JSCover
lib-cov

# Coverage directory used by tools like istanbul
coverage

# nyc test coverage
.nyc_output

# Grunt intermediate storage
.grunt

# Bower dependency directory
bower_components

# node-waf configuration
.lock-wscript

# Compiled binary addons
build/Release

# Dependency directories
node_modules/
jspm_packages/

# TypeScript v1 declaration files
typings/

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# next.js build output
.next

# nuxt.js build output
.nuxt

# vuepress build output
.vuepress/dist

# Serverless directories
.serverless
"""
    
    def _get_web_gitignore(self) -> str:
        """Get Web .gitignore template"""
        return """# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
logs
*.log

# Runtime data
pids
*.pid
*.seed

# Dependency directories
node_modules/
bower_components/

# Build outputs
dist/
build/
.tmp/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
*.tmp
*.temp
"""
    
    # ==================== UTILITY METHODS ====================
    
    def get_github_user_info(self) -> Optional[Dict]:
        """Get authenticated GitHub user information"""
        try:
            if not self.github_token:
                return None
            
            response = requests.get(f"{self.github_api_base}/user", headers=self.github_headers)
            response.raise_for_status()
            
            user_data = response.json()
            
            return {
                'login': user_data['login'],
                'name': user_data.get('name'),
                'email': user_data.get('email'),
                'bio': user_data.get('bio'),
                'public_repos': user_data['public_repos'],
                'followers': user_data['followers'],
                'following': user_data['following'],
                'created_at': user_data['created_at']
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Error getting GitHub user info: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error processing GitHub user info: {e}")
            return None
    
    def search_repositories(self, query: str, sort: str = "updated", order: str = "desc") -> List[Dict]:
        """Search GitHub repositories"""
        try:
            url = f"{self.github_api_base}/search/repositories"
            
            params = {
                "q": query,
                "sort": sort,  # stars, forks, updated
                "order": order,  # asc, desc
                "per_page": 50
            }
            
            response = requests.get(url, headers=self.github_headers, params=params)
            response.raise_for_status()
            
            search_results = response.json()
            repos = search_results.get('items', [])
            
            formatted_repos = []
            for repo in repos:
                formatted_repos.append({
                    'id': repo['id'],
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo.get('description', ''),
                    'html_url': repo['html_url'],
                    'language': repo.get('language'),
                    'stargazers_count': repo['stargazers_count'],
                    'forks_count': repo['forks_count'],
                    'updated_at': repo['updated_at']
                })
            
            self.logger.info(f"Found {len(formatted_repos)} repositories for query: {query}")
            return formatted_repos
            
        except requests.RequestException as e:
            self.logger.error(f"Error searching repositories: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error processing repository search: {e}")
            return []
    
    def is_github_authenticated(self) -> bool:
        """Check if GitHub is authenticated"""
        return self.github_token is not None
    
    def is_vscode_available(self) -> bool:
        """Check if VS Code is available"""
        return self.vscode_path is not None
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get development tools integration status"""
        return {
            'github_authenticated': self.is_github_authenticated(),
            'vscode_available': self.is_vscode_available(),
            'github_token_set': bool(self.github_token),
            'vscode_path': self.vscode_path
        }

# Global development tools instance
dev_tools = DevelopmentToolsIntegration()

