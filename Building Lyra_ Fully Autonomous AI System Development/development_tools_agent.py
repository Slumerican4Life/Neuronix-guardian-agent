"""
Development Tools Agent Integration
=================================

Agent interface for development tools including VS Code, GitHub, and project management.
Provides seamless integration with Lyra's multi-agent system for development workflows.
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

from agents.agent_framework import BaseAgent, AgentMessage, MessageType, AgentCapability
from integrations.development_tools import dev_tools

class DevelopmentToolsAgent(BaseAgent):
    """Agent for development tools integration"""
    
    def __init__(self):
        super().__init__(
            agent_id="development_tools",
            name="DEV_TOOLS",
            description="Development tools integration agent for VS Code, GitHub, and project management"
        )
        
        # Development tools capabilities
        self.add_capability(AgentCapability(
            name="github_management",
            description="Manage GitHub repositories, issues, and pull requests",
            input_types=["github_requests", "repository_data"],
            output_types=["repository_info", "operation_confirmations"],
            resource_requirements={"github_api": "required", "network": "required"},
            execution_time_estimate=8.0
        ))
        
        self.add_capability(AgentCapability(
            name="vscode_control",
            description="Control VS Code editor and workspace management",
            input_types=["vscode_commands", "workspace_data"],
            output_types=["editor_status", "workspace_confirmations"],
            resource_requirements={"vscode": "required", "filesystem": "required"},
            execution_time_estimate=3.0
        ))
        
        self.add_capability(AgentCapability(
            name="project_management",
            description="Create and manage development projects and structures",
            input_types=["project_requests", "structure_data"],
            output_types=["project_info", "creation_confirmations"],
            resource_requirements={"filesystem": "required", "git": "optional"},
            execution_time_estimate=10.0
        ))
        
        self.add_capability(AgentCapability(
            name="git_operations",
            description="Perform Git operations including clone, commit, push, and branch management",
            input_types=["git_commands", "repository_data"],
            output_types=["git_status", "operation_results"],
            resource_requirements={"git": "required", "filesystem": "required"},
            execution_time_estimate=15.0
        ))
        
        # Integration state
        self.github_authenticated = False
        self.vscode_available = False
        self.active_projects = {}
        self.recent_repositories = []
    
    async def initialize(self):
        """Initialize development tools agent"""
        self.logger.info("Initializing Development Tools agent...")
        
        # Check integration status
        status = dev_tools.get_integration_status()
        self.github_authenticated = status['github_authenticated']
        self.vscode_available = status['vscode_available']
        
        if self.github_authenticated:
            self.logger.info("GitHub API authenticated successfully")
            
            # Get user info
            user_info = dev_tools.get_github_user_info()
            if user_info:
                self.logger.info(f"GitHub user: {user_info['login']}")
        else:
            self.logger.warning("GitHub not authenticated - some features will be limited")
        
        if self.vscode_available:
            self.logger.info("VS Code integration available")
        else:
            self.logger.warning("VS Code not available - some features will be limited")
        
        self.logger.info("Development Tools agent initialization complete")
    
    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process incoming messages for development tools operations"""
        try:
            if message.message_type == MessageType.COMMAND:
                return await self._handle_command(message)
            elif message.message_type == MessageType.QUERY:
                return await self._handle_query(message)
            else:
                self.logger.debug(f"Ignoring message type: {message.message_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            return AgentMessage(
                id=f"err_{message.id}",
                sender=self.agent_id,
                recipient=message.sender,
                message_type=MessageType.RESPONSE,
                payload={"error": str(e), "success": False},
                correlation_id=message.correlation_id
            )
    
    async def _handle_command(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle command messages"""
        command = message.payload.get("command")
        parameters = message.payload.get("parameters", {})
        
        # GitHub operations
        if command == "create_repository":
            result = await self._create_repository(parameters)
        elif command == "clone_repository":
            result = await self._clone_repository(parameters)
        elif command == "get_repositories":
            result = await self._get_repositories(parameters)
        elif command == "create_issue":
            result = await self._create_issue(parameters)
        elif command == "create_pull_request":
            result = await self._create_pull_request(parameters)
        elif command == "update_file":
            result = await self._update_file(parameters)
        
        # VS Code operations
        elif command == "open_vscode":
            result = await self._open_vscode(parameters)
        elif command == "install_extension":
            result = await self._install_extension(parameters)
        elif command == "create_workspace":
            result = await self._create_workspace(parameters)
        
        # Project management
        elif command == "create_project":
            result = await self._create_project(parameters)
        elif command == "setup_project_structure":
            result = await self._setup_project_structure(parameters)
        
        # Git operations
        elif command == "git_commit_push":
            result = await self._git_commit_push(parameters)
        elif command == "create_branch":
            result = await self._create_branch(parameters)
        
        else:
            result = {"error": f"Unknown command: {command}", "success": False}
        
        return AgentMessage(
            id=f"resp_{message.id}",
            sender=self.agent_id,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            payload=result,
            correlation_id=message.correlation_id
        )
    
    async def _handle_query(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle query messages"""
        query_type = message.payload.get("query_type")
        
        if query_type == "integration_status":
            result = await self._get_integration_status(message.payload)
        elif query_type == "user_repositories":
            result = await self._get_user_repositories(message.payload)
        elif query_type == "repository_contents":
            result = await self._get_repository_contents(message.payload)
        elif query_type == "repository_issues":
            result = await self._get_repository_issues(message.payload)
        elif query_type == "vscode_extensions":
            result = await self._get_vscode_extensions(message.payload)
        elif query_type == "search_repositories":
            result = await self._search_repositories(message.payload)
        elif query_type == "capabilities":
            result = {"capabilities": list(self.capabilities.keys()), "success": True}
        else:
            result = {"error": f"Unknown query type: {query_type}", "success": False}
        
        return AgentMessage(
            id=f"resp_{message.id}",
            sender=self.agent_id,
            recipient=message.sender,
            message_type=MessageType.RESPONSE,
            payload=result,
            correlation_id=message.correlation_id
        )
    
    # ==================== GITHUB OPERATIONS ====================
    
    async def _create_repository(self, parameters: Dict) -> Dict:
        """Create GitHub repository"""
        try:
            if not self.github_authenticated:
                return {"error": "GitHub not authenticated", "success": False}
            
            name = parameters.get("name")
            description = parameters.get("description", "")
            private = parameters.get("private", False)
            auto_init = parameters.get("auto_init", True)
            gitignore_template = parameters.get("gitignore_template")
            license_template = parameters.get("license_template")
            
            if not name:
                return {"error": "Repository name is required", "success": False}
            
            repo_data = dev_tools.create_repository(
                name=name,
                description=description,
                private=private,
                auto_init=auto_init,
                gitignore_template=gitignore_template,
                license_template=license_template
            )
            
            if repo_data:
                self.logger.info(f"Created repository: {repo_data['full_name']}")
                
                # Add to recent repositories
                self.recent_repositories.insert(0, repo_data)
                self.recent_repositories = self.recent_repositories[:10]  # Keep last 10
                
                return {
                    "success": True,
                    "repository": repo_data
                }
            else:
                return {"error": "Failed to create repository", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error creating repository: {e}")
            return {"error": str(e), "success": False}
    
    async def _clone_repository(self, parameters: Dict) -> Dict:
        """Clone GitHub repository"""
        try:
            repo_url = parameters.get("repo_url")
            local_path = parameters.get("local_path")
            branch = parameters.get("branch")
            
            if not repo_url or not local_path:
                return {"error": "Repository URL and local path are required", "success": False}
            
            success = dev_tools.clone_repository(repo_url, local_path, branch)
            
            if success:
                self.logger.info(f"Cloned repository: {repo_url}")
                
                # Track as active project
                project_name = os.path.basename(local_path)
                self.active_projects[project_name] = {
                    "path": local_path,
                    "repo_url": repo_url,
                    "cloned_at": datetime.now().isoformat()
                }
                
                return {
                    "success": True,
                    "local_path": local_path,
                    "repo_url": repo_url
                }
            else:
                return {"error": "Failed to clone repository", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error cloning repository: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_repositories(self, parameters: Dict) -> Dict:
        """Get user repositories"""
        try:
            if not self.github_authenticated:
                return {"error": "GitHub not authenticated", "success": False}
            
            username = parameters.get("username")
            repo_type = parameters.get("repo_type", "all")
            
            repos = dev_tools.get_user_repositories(username, repo_type)
            
            self.logger.info(f"Retrieved {len(repos)} repositories")
            
            return {
                "success": True,
                "repositories": repos,
                "count": len(repos)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting repositories: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_issue(self, parameters: Dict) -> Dict:
        """Create GitHub issue"""
        try:
            if not self.github_authenticated:
                return {"error": "GitHub not authenticated", "success": False}
            
            owner = parameters.get("owner")
            repo = parameters.get("repo")
            title = parameters.get("title")
            body = parameters.get("body", "")
            labels = parameters.get("labels", [])
            assignees = parameters.get("assignees", [])
            
            if not owner or not repo or not title:
                return {"error": "Owner, repo, and title are required", "success": False}
            
            issue_data = dev_tools.create_issue(owner, repo, title, body, labels, assignees)
            
            if issue_data:
                self.logger.info(f"Created issue: {owner}/{repo}#{issue_data['number']}")
                
                return {
                    "success": True,
                    "issue": issue_data
                }
            else:
                return {"error": "Failed to create issue", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error creating issue: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_pull_request(self, parameters: Dict) -> Dict:
        """Create GitHub pull request"""
        try:
            if not self.github_authenticated:
                return {"error": "GitHub not authenticated", "success": False}
            
            owner = parameters.get("owner")
            repo = parameters.get("repo")
            title = parameters.get("title")
            head = parameters.get("head")
            base = parameters.get("base")
            body = parameters.get("body", "")
            draft = parameters.get("draft", False)
            
            if not all([owner, repo, title, head, base]):
                return {"error": "Owner, repo, title, head, and base are required", "success": False}
            
            pr_data = dev_tools.create_pull_request(owner, repo, title, head, base, body, draft)
            
            if pr_data:
                self.logger.info(f"Created pull request: {owner}/{repo}#{pr_data['number']}")
                
                return {
                    "success": True,
                    "pull_request": pr_data
                }
            else:
                return {"error": "Failed to create pull request", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error creating pull request: {e}")
            return {"error": str(e), "success": False}
    
    async def _update_file(self, parameters: Dict) -> Dict:
        """Update file in GitHub repository"""
        try:
            if not self.github_authenticated:
                return {"error": "GitHub not authenticated", "success": False}
            
            owner = parameters.get("owner")
            repo = parameters.get("repo")
            path = parameters.get("path")
            content = parameters.get("content")
            message = parameters.get("message")
            branch = parameters.get("branch", "main")
            
            if not all([owner, repo, path, content, message]):
                return {"error": "Owner, repo, path, content, and message are required", "success": False}
            
            # Get existing file SHA if updating
            existing_content = dev_tools.get_file_content(owner, repo, path)
            sha = None
            
            if existing_content is not None:
                # File exists, get SHA for update
                contents = dev_tools.get_repository_contents(owner, repo, path)
                if contents:
                    sha = contents[0]['sha']
            
            result = dev_tools.create_or_update_file(owner, repo, path, content, message, branch, sha)
            
            if result:
                action = "Updated" if sha else "Created"
                self.logger.info(f"{action} file: {owner}/{repo}/{path}")
                
                return {
                    "success": True,
                    "action": action.lower(),
                    "file_data": result
                }
            else:
                return {"error": "Failed to update file", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error updating file: {e}")
            return {"error": str(e), "success": False}
    
    # ==================== VS CODE OPERATIONS ====================
    
    async def _open_vscode(self, parameters: Dict) -> Dict:
        """Open VS Code"""
        try:
            if not self.vscode_available:
                return {"error": "VS Code not available", "success": False}
            
            path = parameters.get("path")
            new_window = parameters.get("new_window", False)
            
            success = dev_tools.open_vscode(path, new_window)
            
            if success:
                self.logger.info(f"Opened VS Code: {path or 'default'}")
                
                return {
                    "success": True,
                    "path": path,
                    "new_window": new_window
                }
            else:
                return {"error": "Failed to open VS Code", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error opening VS Code: {e}")
            return {"error": str(e), "success": False}
    
    async def _install_extension(self, parameters: Dict) -> Dict:
        """Install VS Code extension"""
        try:
            if not self.vscode_available:
                return {"error": "VS Code not available", "success": False}
            
            extension_id = parameters.get("extension_id")
            
            if not extension_id:
                return {"error": "Extension ID is required", "success": False}
            
            success = dev_tools.install_vscode_extension(extension_id)
            
            if success:
                self.logger.info(f"Installed VS Code extension: {extension_id}")
                
                return {
                    "success": True,
                    "extension_id": extension_id
                }
            else:
                return {"error": "Failed to install extension", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error installing extension: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_workspace(self, parameters: Dict) -> Dict:
        """Create VS Code workspace"""
        try:
            workspace_path = parameters.get("workspace_path")
            folders = parameters.get("folders", [])
            settings = parameters.get("settings", {})
            extensions = parameters.get("extensions", {})
            
            if not workspace_path:
                return {"error": "Workspace path is required", "success": False}
            
            success = dev_tools.create_vscode_workspace(workspace_path, folders, settings, extensions)
            
            if success:
                self.logger.info(f"Created VS Code workspace: {workspace_path}")
                
                return {
                    "success": True,
                    "workspace_path": workspace_path,
                    "folders": folders
                }
            else:
                return {"error": "Failed to create workspace", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error creating workspace: {e}")
            return {"error": str(e), "success": False}
    
    # ==================== PROJECT MANAGEMENT ====================
    
    async def _create_project(self, parameters: Dict) -> Dict:
        """Create development project"""
        try:
            project_name = parameters.get("project_name")
            project_path = parameters.get("project_path")
            project_type = parameters.get("project_type", "python")
            initialize_git = parameters.get("initialize_git", True)
            create_github_repo = parameters.get("create_github_repo", False)
            
            if not project_name:
                return {"error": "Project name is required", "success": False}
            
            if not project_path:
                project_path = f"./{project_name}"
            
            # Create project structure
            success = dev_tools.create_project_structure(project_path, project_type)
            
            if not success:
                return {"error": "Failed to create project structure", "success": False}
            
            project_info = {
                "name": project_name,
                "path": project_path,
                "type": project_type,
                "created_at": datetime.now().isoformat()
            }
            
            # Initialize Git if requested
            if initialize_git:
                try:
                    import subprocess
                    subprocess.run(["git", "init"], cwd=project_path, check=True)
                    project_info["git_initialized"] = True
                    self.logger.info(f"Initialized Git repository in {project_path}")
                except Exception as e:
                    self.logger.warning(f"Failed to initialize Git: {e}")
                    project_info["git_initialized"] = False
            
            # Create GitHub repository if requested
            if create_github_repo and self.github_authenticated:
                repo_data = dev_tools.create_repository(
                    name=project_name,
                    description=f"Auto-created {project_type} project",
                    private=False,
                    auto_init=False
                )
                
                if repo_data:
                    project_info["github_repo"] = repo_data
                    self.logger.info(f"Created GitHub repository: {repo_data['full_name']}")
            
            # Track as active project
            self.active_projects[project_name] = project_info
            
            self.logger.info(f"Created project: {project_name}")
            
            return {
                "success": True,
                "project": project_info
            }
            
        except Exception as e:
            self.logger.error(f"Error creating project: {e}")
            return {"error": str(e), "success": False}
    
    async def _setup_project_structure(self, parameters: Dict) -> Dict:
        """Setup project structure"""
        try:
            project_path = parameters.get("project_path")
            project_type = parameters.get("project_type", "python")
            
            if not project_path:
                return {"error": "Project path is required", "success": False}
            
            success = dev_tools.create_project_structure(project_path, project_type)
            
            if success:
                self.logger.info(f"Setup project structure: {project_path}")
                
                return {
                    "success": True,
                    "project_path": project_path,
                    "project_type": project_type
                }
            else:
                return {"error": "Failed to setup project structure", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error setting up project structure: {e}")
            return {"error": str(e), "success": False}
    
    # ==================== GIT OPERATIONS ====================
    
    async def _git_commit_push(self, parameters: Dict) -> Dict:
        """Git commit and push"""
        try:
            repo_path = parameters.get("repo_path")
            message = parameters.get("message")
            files = parameters.get("files")
            branch = parameters.get("branch")
            push = parameters.get("push", True)
            
            if not repo_path or not message:
                return {"error": "Repository path and commit message are required", "success": False}
            
            success = dev_tools.git_commit_and_push(repo_path, message, files, branch, push)
            
            if success:
                self.logger.info(f"Git commit and push successful: {message}")
                
                return {
                    "success": True,
                    "message": message,
                    "repo_path": repo_path,
                    "pushed": push
                }
            else:
                return {"error": "Failed to commit and push", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error in git commit/push: {e}")
            return {"error": str(e), "success": False}
    
    async def _create_branch(self, parameters: Dict) -> Dict:
        """Create Git branch"""
        try:
            repo_path = parameters.get("repo_path")
            branch_name = parameters.get("branch_name")
            checkout = parameters.get("checkout", True)
            
            if not repo_path or not branch_name:
                return {"error": "Repository path and branch name are required", "success": False}
            
            success = dev_tools.create_git_branch(repo_path, branch_name, checkout)
            
            if success:
                self.logger.info(f"Created Git branch: {branch_name}")
                
                return {
                    "success": True,
                    "branch_name": branch_name,
                    "repo_path": repo_path,
                    "checked_out": checkout
                }
            else:
                return {"error": "Failed to create branch", "success": False}
                
        except Exception as e:
            self.logger.error(f"Error creating branch: {e}")
            return {"error": str(e), "success": False}
    
    # ==================== QUERY OPERATIONS ====================
    
    async def _get_integration_status(self, parameters: Dict) -> Dict:
        """Get integration status"""
        try:
            status = dev_tools.get_integration_status()
            
            return {
                "success": True,
                "integration_status": status,
                "active_projects": len(self.active_projects),
                "recent_repositories": len(self.recent_repositories)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_user_repositories(self, parameters: Dict) -> Dict:
        """Get user repositories"""
        try:
            if not self.github_authenticated:
                return {"error": "GitHub not authenticated", "success": False}
            
            username = parameters.get("username")
            repo_type = parameters.get("repo_type", "all")
            
            repos = dev_tools.get_user_repositories(username, repo_type)
            
            return {
                "success": True,
                "repositories": repos,
                "count": len(repos)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user repositories: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_repository_contents(self, parameters: Dict) -> Dict:
        """Get repository contents"""
        try:
            if not self.github_authenticated:
                return {"error": "GitHub not authenticated", "success": False}
            
            owner = parameters.get("owner")
            repo = parameters.get("repo")
            path = parameters.get("path", "")
            
            if not owner or not repo:
                return {"error": "Owner and repo are required", "success": False}
            
            contents = dev_tools.get_repository_contents(owner, repo, path)
            
            return {
                "success": True,
                "contents": contents,
                "count": len(contents)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting repository contents: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_repository_issues(self, parameters: Dict) -> Dict:
        """Get repository issues"""
        try:
            if not self.github_authenticated:
                return {"error": "GitHub not authenticated", "success": False}
            
            owner = parameters.get("owner")
            repo = parameters.get("repo")
            state = parameters.get("state", "open")
            
            if not owner or not repo:
                return {"error": "Owner and repo are required", "success": False}
            
            issues = dev_tools.get_repository_issues(owner, repo, state)
            
            return {
                "success": True,
                "issues": issues,
                "count": len(issues)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting repository issues: {e}")
            return {"error": str(e), "success": False}
    
    async def _get_vscode_extensions(self, parameters: Dict) -> Dict:
        """Get VS Code extensions"""
        try:
            if not self.vscode_available:
                return {"error": "VS Code not available", "success": False}
            
            extensions = dev_tools.list_vscode_extensions()
            
            return {
                "success": True,
                "extensions": extensions,
                "count": len(extensions)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting VS Code extensions: {e}")
            return {"error": str(e), "success": False}
    
    async def _search_repositories(self, parameters: Dict) -> Dict:
        """Search GitHub repositories"""
        try:
            query = parameters.get("query")
            sort = parameters.get("sort", "updated")
            order = parameters.get("order", "desc")
            
            if not query:
                return {"error": "Search query is required", "success": False}
            
            repos = dev_tools.search_repositories(query, sort, order)
            
            return {
                "success": True,
                "repositories": repos,
                "count": len(repos),
                "query": query
            }
            
        except Exception as e:
            self.logger.error(f"Error searching repositories: {e}")
            return {"error": str(e), "success": False}
    
    async def shutdown(self):
        """Shutdown development tools agent"""
        self.logger.info("Shutting down Development Tools agent...")
        
        # Save state
        try:
            state_data = {
                "active_projects": self.active_projects,
                "recent_repositories": self.recent_repositories,
                "github_authenticated": self.github_authenticated,
                "vscode_available": self.vscode_available
            }
            
            with open("integrations/dev_tools_state.json", "w") as f:
                json.dump(state_data, f, indent=2)
                
            self.logger.info("Development tools state saved successfully")
        except Exception as e:
            self.logger.error(f"Error saving development tools state: {e}")

# Create development tools agent instance
dev_tools_agent = DevelopmentToolsAgent()

