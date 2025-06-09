# Development Tools Setup Instructions

## Overview
The Development Tools integration provides Lyra with comprehensive development capabilities:
- **GitHub Integration**: Repository management, issues, pull requests, file operations
- **VS Code Control**: Editor automation, workspace management, extension handling
- **Project Management**: Automated project creation with standard structures
- **Git Operations**: Clone, commit, push, branch management

## Setup Process

### 1. GitHub Integration Setup

#### Create GitHub Personal Access Token
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` - Full repository access
   - `user` - User profile access
   - `admin:org` - Organization access (if needed)
   - `workflow` - GitHub Actions (if needed)
4. Copy the generated token

#### Configure Token
```bash
# Set environment variable
export GITHUB_TOKEN="your_token_here"

# Or pass directly to integration
dev_tools = DevelopmentToolsIntegration(github_token="your_token_here")
```

### 2. VS Code Integration Setup

#### Install VS Code
```bash
# Ubuntu/Debian
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/
sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
sudo apt update
sudo apt install code

# Or via Snap
sudo snap install code --classic
```

#### Verify Installation
```bash
code --version
```

### 3. Git Configuration
```bash
# Configure Git (required for operations)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Usage Examples

### GitHub Operations
```python
# Create repository
repo_data = dev_tools.create_repository(
    name="my-new-project",
    description="A new project created by Lyra",
    private=False,
    auto_init=True,
    gitignore_template="Python"
)

# Clone repository
success = dev_tools.clone_repository(
    repo_url="https://github.com/user/repo.git",
    local_path="./my-project"
)

# Create issue
issue = dev_tools.create_issue(
    owner="username",
    repo="repository",
    title="Bug report",
    body="Description of the issue",
    labels=["bug", "priority-high"]
)

# Update file
result = dev_tools.create_or_update_file(
    owner="username",
    repo="repository",
    path="README.md",
    content="# Updated README",
    message="Update README file"
)
```

### VS Code Operations
```python
# Open VS Code with project
success = dev_tools.open_vscode("/path/to/project")

# Install extension
success = dev_tools.install_vscode_extension("ms-python.python")

# Create workspace
success = dev_tools.create_vscode_workspace(
    workspace_path="./my-workspace.code-workspace",
    folders=["./src", "./tests"],
    settings={
        "python.defaultInterpreterPath": "./venv/bin/python"
    }
)
```

### Project Management
```python
# Create Python project
success = dev_tools.create_project_structure(
    project_path="./my-python-project",
    project_type="python"
)

# Create JavaScript project
success = dev_tools.create_project_structure(
    project_path="./my-js-project",
    project_type="javascript"
)
```

### Git Operations
```python
# Commit and push changes
success = dev_tools.git_commit_and_push(
    repo_path="./my-project",
    message="Add new feature",
    files=["src/new_feature.py"],
    push=True
)

# Create branch
success = dev_tools.create_git_branch(
    repo_path="./my-project",
    branch_name="feature/new-feature",
    checkout=True
)
```

## Agent Integration

The Development Tools Agent provides seamless integration with Lyra's multi-agent system:

```python
# Through agent system
await lyra_agent_manager.send_command('development_tools', 'create_project', {
    'project_name': 'lyra-extension',
    'project_type': 'python',
    'initialize_git': True,
    'create_github_repo': True
})

# Query repositories
repos = await lyra_agent_manager.send_query('development_tools', 'user_repositories', {
    'repo_type': 'owner'
})
```

## Supported Project Types

### Python Projects
- `src/` - Source code
- `tests/` - Test files
- `docs/` - Documentation
- `scripts/` - Utility scripts
- `requirements.txt` - Dependencies
- `setup.py` - Package setup
- `.gitignore` - Python-specific ignores

### JavaScript Projects
- `src/` - Source code
- `test/` - Test files
- `docs/` - Documentation
- `public/` - Public assets
- `package.json` - Package configuration
- `.gitignore` - Node.js-specific ignores

### Web Projects
- `src/` - Source code
- `assets/` - Static assets
- `css/` - Stylesheets
- `js/` - JavaScript files
- `images/` - Image assets
- `index.html` - Main HTML file
- `.gitignore` - Web-specific ignores

## Advanced Features

### Automated Workflows
```python
# Complete project setup workflow
async def create_full_project(name, type="python"):
    # Create local project
    dev_tools.create_project_structure(f"./{name}", type)
    
    # Initialize Git
    dev_tools.git_commit_and_push(f"./{name}", "Initial commit", push=False)
    
    # Create GitHub repo
    repo = dev_tools.create_repository(name, f"Auto-created {type} project")
    
    # Connect local to remote
    subprocess.run(["git", "remote", "add", "origin", repo['clone_url']], 
                   cwd=f"./{name}")
    
    # Push to GitHub
    dev_tools.git_commit_and_push(f"./{name}", "Initial commit", push=True)
    
    # Open in VS Code
    dev_tools.open_vscode(f"./{name}")
    
    return repo
```

### Repository Search and Analysis
```python
# Search for repositories
repos = dev_tools.search_repositories("machine learning python", sort="stars")

# Analyze repository structure
contents = dev_tools.get_repository_contents("owner", "repo")
for item in contents:
    if item['type'] == 'file' and item['name'].endswith('.py'):
        content = dev_tools.get_file_content("owner", "repo", item['path'])
        # Analyze Python code
```

## Security Notes

1. **Token Security**: Never commit GitHub tokens to repositories
2. **Scope Limitation**: Only grant necessary permissions to tokens
3. **Token Rotation**: Regularly rotate access tokens
4. **Audit Logging**: All operations are logged for security monitoring

## Troubleshooting

### Common Issues
1. **"GitHub not authenticated"**: Set GITHUB_TOKEN environment variable
2. **"VS Code not available"**: Install VS Code and ensure it's in PATH
3. **"Git operation failed"**: Configure Git user name and email
4. **"Permission denied"**: Check GitHub token permissions

### Error Handling
The integration includes comprehensive error handling:
- GitHub API errors and rate limiting
- VS Code process failures
- Git operation errors
- File system permission issues

## Production Deployment

For production use:
1. Use GitHub Apps instead of personal tokens for organization access
2. Implement proper secret management for tokens
3. Set up monitoring and alerting for failed operations
4. Configure backup authentication methods
5. Implement rate limiting and retry logic

