# Demo Agent Implementation Plan

## 🎯 Project Overview

**Demo Agent** is a specialized automation system built on top of the Open Computer Use framework that performs automated developer demonstrations via screen sharing on Google Meet. The agent clones a GitHub repository, opens it in a code editor, joins a Google Meet call, and shares the screen for live coding demonstrations.

## 📋 Requirements

### Input Parameters
- **githubUrl**: Valid HTTPS GitHub repository URL (e.g., `https://github.com/user/repo.git`)
- **meetLink**: Valid Google Meet URL (e.g., `https://meet.google.com/abc-defg-hij`)

### Expected Workflow
1. **Launch E2B Desktop Sandbox**
2. **Execute Sequential Actions**:
   - Open terminal application
   - Clone the specified GitHub repository
   - Navigate into the repository folder
   - Open code viewer (VS Code preferred, fallback to file listing)
   - Launch web browser
   - Navigate to Google Meet link
   - Join call as guest with name "demo-agent"
   - Start screen sharing (entire screen)
   - Wait for further instructions

### Output Requirements
- Step-by-step execution logs
- Sandbox desktop UI link for monitoring
- Real-time progress tracking
- Error handling and recovery

## 🏗️ Technical Architecture

### Core Components

#### 1. Demo Agent Class (`os_computer_use/demo_agent.py`)
```python
class DemoAgent(APISandboxAgent):
    """
    Specialized agent for automated demo presentations
    Extends APISandboxAgent with demo-specific capabilities
    """
    
    async def run_demo_session(self, github_url: str, meet_link: str) -> dict
    async def execute_step(self, step_name: str, **kwargs) -> dict
    def validate_inputs(self, github_url: str, meet_link: str) -> bool
    def get_sandbox_url(self) -> str
    def get_progress_status(self) -> dict
```

#### 2. Action Orchestrator (`os_computer_use/demo_orchestrator.py`)
```python
class DemoOrchestrator:
    """
    Manages the sequential execution of demo steps
    Handles retries, error recovery, and progress tracking
    """
    
    def __init__(self, agent: DemoAgent)
    async def run_full_demo(self, github_url: str, meet_link: str) -> dict
    async def execute_with_retry(self, action: str, max_retries: int = 3) -> dict
    def log_step_completion(self, step: str, success: bool, details: str)
    def get_execution_summary(self) -> dict
```

#### 3. Specialized Actions (`os_computer_use/demo_actions.py`)
```python
class DemoActions:
    """
    Individual action implementations for demo workflow
    """
    
    async def open_terminal(self) -> dict
    async def clone_repository(self, github_url: str) -> dict
    async def navigate_to_repo(self, github_url: str) -> dict
    async def open_code_viewer(self) -> dict
    async def open_browser(self) -> dict
    async def join_meet_call(self, meet_link: str) -> dict
    async def start_screen_share(self) -> dict
    async def wait_for_instructions(self) -> dict
```

#### 4. Prompt Engineering (`os_computer_use/demo_prompts.py`)
```python
class DemoPrompts:
    """
    Optimized prompts for each demo step
    Includes fallback prompts and error recovery instructions
    """
    
    TERMINAL_PROMPT = "..."
    GIT_CLONE_PROMPT = "..."
    NAVIGATION_PROMPT = "..."
    CODE_VIEWER_PROMPT = "..."
    BROWSER_PROMPT = "..."
    MEET_JOIN_PROMPT = "..."
    SCREEN_SHARE_PROMPT = "..."
    WAIT_PROMPT = "..."
```

## 🔧 Implementation Plan

### Phase 1: Core Infrastructure (Files to Create/Modify)

#### 1.1 Create Demo Agent Infrastructure
- **File**: `os_computer_use/demo_agent.py`
- **Purpose**: Main demo agent class extending APISandboxAgent
- **Key Features**:
  - Async operation support
  - Step validation and error handling
  - Progress tracking with timestamps
  - Sandbox URL provisioning

#### 1.2 Create Action Orchestrator
- **File**: `os_computer_use/demo_orchestrator.py`
- **Purpose**: Manages sequential execution of demo steps
- **Key Features**:
  - Retry logic with exponential backoff
  - Step dependency management
  - Comprehensive logging
  - Execution state persistence

#### 1.3 Implement Specialized Actions
- **File**: `os_computer_use/demo_actions.py`
- **Purpose**: Individual action implementations
- **Key Features**:
  - Robust error handling for each action
  - Visual confirmation of success
  - Fallback strategies for UI variations
  - Timeout management

#### 1.4 Create Optimized Prompts
- **File**: `os_computer_use/demo_prompts.py`
- **Purpose**: Specialized prompts for each demo step
- **Key Features**:
  - Context-aware instructions
  - Visual element descriptions
  - Error recovery guidance
  - Alternative action prompts

### Phase 2: API Integration

#### 2.1 Add Demo Endpoint to API Server
- **File**: `api_server.py` (modify existing)
- **New Endpoint**: `POST /demo-session`
- **Features**:
  - Input validation for GitHub URL and Meet link
  - Session management and tracking
  - Real-time progress updates
  - Error handling and recovery

#### 2.2 Add Progress Tracking Endpoint
- **File**: `api_server.py` (modify existing)
- **New Endpoint**: `GET /demo-session/{sessionId}/status`
- **Features**:
  - Real-time status updates
  - Step completion tracking
  - Log retrieval
  - Sandbox URL access

#### 2.3 Session Management
- **File**: `os_computer_use/demo_session.py`
- **Purpose**: Manage demo session lifecycle
- **Features**:
  - Session state persistence
  - Cleanup on completion/failure
  - Resource management
  - Progress snapshots

### Phase 3: Enhanced Features

#### 3.1 Create Node.js Client
- **File**: `nodejs_client_demo.js`
- **Purpose**: Simplified client for demo agent
- **Features**:
  - Demo session management
  - Progress monitoring
  - Error handling
  - Webhook support for updates

#### 3.2 Add WebSocket Support
- **File**: `api_server.py` (modify existing)
- **Purpose**: Real-time progress updates
- **Features**:
  - Live step execution updates
  - Screenshot streaming
  - Error notifications
  - Session state changes

#### 3.3 Configuration Management
- **File**: `os_computer_use/demo_config.py`
- **Purpose**: Demo-specific configuration
- **Features**:
  - Timeout settings per step
  - Retry configurations
  - Model selection optimization
  - Environment-specific settings

## 📊 Data Flow

### 1. Session Initialization
```
Client Request → Input Validation → Sandbox Creation → Agent Initialization
```

### 2. Step Execution
```
Step Start → Prompt Generation → LLM Call → Action Execution → Validation → Logging
```

### 3. Progress Tracking
```
Step Completion → Status Update → Client Notification → Next Step Trigger
```

### 4. Error Handling
```
Error Detection → Recovery Attempt → Fallback Strategy → User Notification
```

## 🎭 Detailed Step Breakdown

### Step 1: Open Terminal
- **Action**: Launch terminal application
- **Prompt**: "Open the terminal application on the desktop"
- **Validation**: Verify terminal window is visible
- **Fallback**: Try different terminal applications (gnome-terminal, xterm, konsole)
- **Timeout**: 30 seconds

### Step 2: Clone Repository
- **Action**: Execute `git clone {github_url}`
- **Prompt**: "In the terminal, run the git clone command for the repository"
- **Validation**: Check for successful clone message and directory creation
- **Fallback**: Retry with different clone options (--depth=1, --single-branch)
- **Timeout**: 120 seconds

### Step 3: Navigate to Repository
- **Action**: Execute `cd $(basename {github_url} .git)`
- **Prompt**: "Navigate into the cloned repository directory"
- **Validation**: Verify current directory change
- **Fallback**: Manual directory navigation with ls and cd
- **Timeout**: 30 seconds

### Step 4: Open Code Viewer
- **Action**: Try `code .` then fallback to `ls -la`
- **Prompt**: "Open VS Code in the current directory, or list files if VS Code is not available"
- **Validation**: VS Code window appears or file listing is displayed
- **Fallback**: Use alternative editors (nano, vim, gedit)
- **Timeout**: 60 seconds

### Step 5: Open Browser
- **Action**: Launch web browser
- **Prompt**: "Open a web browser (Firefox or Chrome)"
- **Validation**: Browser window is visible
- **Fallback**: Try different browsers in order of preference
- **Timeout**: 45 seconds

### Step 6: Join Meet Call
- **Action**: Navigate to Meet link and join as guest
- **Prompt**: "Navigate to the Google Meet link and join the call as a guest named 'demo-agent'"
- **Validation**: Successfully joined the call (participant visible)
- **Fallback**: Handle different Meet UI variations
- **Timeout**: 180 seconds

### Step 7: Start Screen Share
- **Action**: Click "Present now" → "Your entire screen" → Confirm
- **Prompt**: "Start screen sharing by clicking Present now, select entire screen, and confirm"
- **Validation**: Screen sharing indicator is visible
- **Fallback**: Handle browser permission dialogs
- **Timeout**: 120 seconds

### Step 8: Wait for Instructions
- **Action**: Enter idle state with periodic status checks
- **Prompt**: "Wait for further instructions while maintaining the screen share"
- **Validation**: Screen sharing remains active
- **Fallback**: Reconnect if connection is lost
- **Timeout**: Indefinite (user-controlled)

## 🚨 Error Handling Strategy

### Input Validation Errors
- **GitHub URL**: Validate format and accessibility
- **Meet Link**: Validate Google Meet URL format
- **Response**: Return clear error messages with suggested fixes

### Execution Errors
- **Network Issues**: Retry with exponential backoff
- **UI Element Not Found**: Use alternative selectors or fallback actions
- **Application Crashes**: Restart applications and retry
- **Permission Denied**: Provide clear instructions for manual intervention

### Recovery Strategies
- **Partial Failure**: Continue from the last successful step
- **Complete Failure**: Offer manual intervention points
- **Timeout Exceeded**: Extend timeout or skip to next step
- **Resource Exhaustion**: Clean up and restart sandbox

## 📈 Success Metrics

### Completion Rates
- **Full Demo Success**: All 8 steps completed successfully
- **Partial Success**: At least 6 steps completed
- **Critical Path Success**: Steps 1-6 completed (minimal viable demo)

### Performance Metrics
- **Total Execution Time**: Target < 5 minutes
- **Step Success Rate**: Target > 90% per step
- **Error Recovery Rate**: Target > 80% of recoverable errors
- **User Satisfaction**: Monitoring via feedback

## 🔒 Security Considerations

### Sandbox Security
- **Isolated Environment**: All operations in E2B sandbox
- **Resource Limits**: CPU, memory, and network restrictions
- **Session Cleanup**: Automatic cleanup after completion/timeout

### Data Privacy
- **No Persistent Storage**: Temporary file storage only
- **Screen Share Content**: User awareness of shared content
- **Meet Call Recording**: Disclaimer about potential recording

### Access Control
- **API Authentication**: Required for demo session creation
- **Rate Limiting**: Prevent abuse of demo functionality
- **Session Management**: Unique session IDs and expiration

## 🧪 Testing Strategy

### Unit Tests
- **Individual Actions**: Test each step in isolation
- **Error Handling**: Verify error recovery mechanisms
- **Input Validation**: Test various input formats
- **Timeout Handling**: Verify timeout behavior

### Integration Tests
- **Full Demo Flow**: End-to-end testing with real repositories
- **Error Scenarios**: Test with invalid URLs and network issues
- **Browser Compatibility**: Test with different browsers
- **Meet UI Variations**: Test with different Meet interfaces

### Performance Tests
- **Load Testing**: Multiple concurrent demo sessions
- **Resource Usage**: Monitor sandbox resource consumption
- **Timeout Optimization**: Find optimal timeout values
- **Scaling**: Test with various repository sizes

## 📚 Documentation Requirements

### API Documentation
- **Endpoint Specifications**: Request/response formats
- **Error Codes**: Comprehensive error code reference
- **Rate Limits**: Usage limitations and guidelines
- **Authentication**: API key requirements

### User Guide
- **Getting Started**: Step-by-step setup instructions
- **Troubleshooting**: Common issues and solutions
- **Best Practices**: Optimal usage patterns
- **Examples**: Sample implementations

### Developer Guide
- **Architecture Overview**: System design explanation
- **Extension Points**: How to add new features
- **Configuration**: Environment setup and customization
- **Debugging**: Logging and troubleshooting tools

## 🚀 Future Enhancements

### Advanced Features
- **Multi-Repository Support**: Handle multiple repos in one session
- **Custom Presentation Scripts**: User-defined demonstration flows
- **Recording Capabilities**: Automated demo recording
- **Interactive Elements**: Real-time interaction during demos

### AI Improvements
- **Adaptive Prompting**: Learn from successful/failed attempts
- **Context Awareness**: Better understanding of application states
- **Predictive Actions**: Anticipate next steps based on context
- **Natural Language Commands**: Accept free-form instructions

### Integration Enhancements
- **Slack/Discord Bots**: Direct integration with team communication
- **CI/CD Pipeline**: Automated demo generation on code changes
- **Presentation Platforms**: Integration with Zoom, Teams, etc.
- **Analytics Dashboard**: Demo performance and usage analytics

## 📅 Implementation Timeline

### Week 1: Core Infrastructure
- [ ] Create demo agent class
- [ ] Implement action orchestrator
- [ ] Build specialized actions
- [ ] Create optimized prompts

### Week 2: API Integration
- [ ] Add demo endpoints to API server
- [ ] Implement session management
- [ ] Add progress tracking
- [ ] Create error handling

### Week 3: Enhanced Features
- [ ] Build Node.js client
- [ ] Add WebSocket support
- [ ] Implement configuration management
- [ ] Create comprehensive logging

### Week 4: Testing & Documentation
- [ ] Unit and integration tests
- [ ] Performance optimization
- [ ] Documentation completion
- [ ] Final testing and debugging

## 🎯 Success Criteria

### Functional Requirements
- ✅ Successfully clone any public GitHub repository
- ✅ Join Google Meet calls as guest
- ✅ Start screen sharing reliably
- ✅ Handle common error scenarios gracefully
- ✅ Provide real-time progress updates

### Non-Functional Requirements
- ✅ Complete demo setup in under 5 minutes
- ✅ 90%+ success rate for individual steps
- ✅ Comprehensive error reporting
- ✅ Clean API interface for integration
- ✅ Detailed logging for debugging

### User Experience
- ✅ Intuitive API design
- ✅ Clear error messages
- ✅ Real-time progress feedback
- ✅ Reliable sandbox monitoring
- ✅ Graceful failure handling

---

## 📝 Next Steps

1. **Review and Approve Plan**: Confirm all requirements are captured
2. **Begin Implementation**: Start with Phase 1 core infrastructure
3. **Iterative Development**: Build and test incrementally
4. **User Feedback**: Gather feedback during development
5. **Production Deployment**: Launch with monitoring and support

This plan provides a comprehensive roadmap for implementing the Demo Agent functionality while maintaining the high quality and reliability standards of the Open Computer Use project.
