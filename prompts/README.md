# Prompts Directory

This directory contains organized prompts for the multi-agent system, including system prompts, task prompts, templates, and examples.

## Directory Structure

```
prompts/
├── system/           # System prompts for agent personalities
│   ├── analyst.md    # Data analyst agent system prompt
│   ├── researcher.md # Research agent system prompt
│   └── coordinator.md# Coordinator agent system prompt
├── task/             # Task-specific prompt templates
│   ├── data_analysis.md
│   ├── research.md
│   └── coordination.md
├── templates/        # General-purpose prompt templates
│   └── basic_task.md
├── examples/         # Example prompts with real data
│   └── sales_analysis.md
└── README.md         # This file
```

## Prompt Types

### System Prompts (`/system/`)
Define the personality, role, and behavior of AI agents. These are loaded when creating agents and establish their core capabilities and communication style.

**Features:**
- Define agent personality and expertise
- Set communication style and standards
- Establish quality criteria and best practices
- Configure collaboration protocols

**Usage:**
```python
from prompt_loader import load_system_prompt
system_prompt = load_system_prompt("analyst")
agent = AIAgent("Data-Analyst", broker, system_prompt)
```

### Task Prompts (`/task/`)
Template prompts for specific types of tasks. These include variable placeholders that can be filled in with specific task data.

**Features:**
- Structured task specifications
- Variable placeholders for customization
- Quality checklists and frameworks
- Expected output definitions

**Usage:**
```python
from prompt_loader import PromptLoader
loader = PromptLoader()
template = loader.create_prompt_template("data_analysis", "task")
```

### Templates (`/templates/`)
General-purpose prompt templates that can be adapted for various use cases.

**Features:**
- Flexible, reusable structures
- Common prompt patterns
- Basic task frameworks
- Customizable for different domains

### Examples (`/examples/`)
Complete, real-world examples showing how to use prompts with actual data.

**Features:**
- Real-world scenarios
- Complete task specifications
- Example data and requirements
- Expected output examples

## Variable Substitution

Prompts support variable substitution using curly braces `{variable_name}`. Variables are automatically detected and can be filled in when creating prompts.

**Example:**
```markdown
## Task Details
- **Task Name**: {task_name}
- **Priority**: {priority}
- **Deadline**: {deadline}

## Data Information
- **Dataset**: {dataset}
- **Analysis Type**: {analysis_type}
```

**Usage:**
```python
prompt = loader.create_prompt(
    "data_analysis",
    "task",
    task_name="Q4 Sales Analysis",
    priority="High",
    deadline="2024-01-15",
    dataset="sales_q4_2023.csv",
    analysis_type="Performance Analysis"
)
```

## Using the Prompt Loader

### Basic Usage

```python
from prompt_loader import PromptLoader

# Initialize loader
loader = PromptLoader()

# Load system prompt
system_prompt = loader.get_system_prompt("analyst")

# Load task template
task_template = loader.create_prompt_template("data_analysis", "task")

# Create custom prompt from template
custom_prompt = loader.create_prompt(
    "data_analysis",
    "task",
    task_name="My Analysis",
    dataset="my_data.csv"
)
```

### Advanced Features

```python
# Search prompts
analysis_prompts = loader.search_prompts("analysis")

# Get prompt metadata
info = loader.get_prompt_info("analyst")

# Export all prompts
loader.export_prompts("backup.json")

# Get statistics
stats = loader.get_statistics()
```

## Creating New Prompts

### System Prompt Template

```markdown
# [Agent Type] System Prompt

You are an [agent role description]. Your role is to:

## Core Responsibilities
1. **[Responsibility 1]**: [Description]
2. **[Responsibility 2]**: [Description]

## Key Capabilities
- **[Capability 1]**: [Description]
- **[Capability 2]**: [Description]

## Communication Style
- **[Style Aspect 1]**: [Description]
- **[Style Aspect 2]**: [Description]

## Quality Standards
- [Standard 1]
- [Standard 2]

## Collaboration
- [Collaboration guideline 1]
- [Collaboration guideline 2]

Remember: [Key reminder about the agent's purpose]
```

### Task Prompt Template

```markdown
# [Task Type] Task Prompt Template

You are tasked with [task description]. Please [action] according to the specifications below:

## Task Details
- **Task Name**: {task_name}
- **Task Type**: {task_type}
- **Priority**: {priority}
- **Deadline**: {deadline}

## Requirements
- **[Requirement Category]**: {requirement_variable}
- **[Another Category]**: {another_variable}

## Specific Instructions
{specific_instructions}

## Framework
1. **[Step 1]**: [Description]
2. **[Step 2]**: [Description]

## Quality Checklist
- [ ] [Quality criterion 1]
- [ ] [Quality criterion 2]

## Expected Output
[Description of expected deliverables]

Please ensure [quality requirement] and provide [specific output format].
```

## Best Practices

### Writing Effective Prompts

1. **Be Specific**: Clearly define expectations and requirements
2. **Use Structure**: Organize prompts with clear sections and headings
3. **Include Examples**: Provide concrete examples where helpful
4. **Define Quality**: Specify quality criteria and success metrics
5. **Consider Context**: Include relevant background information
6. **Use Variables**: Make prompts reusable with variable substitution

### Managing Prompts

1. **Consistent Naming**: Use clear, descriptive file names
2. **Version Control**: Track changes to prompts over time
3. **Documentation**: Document prompt purpose and usage
4. **Testing**: Test prompts with real data before deployment
5. **Organization**: Keep related prompts grouped together

### Variable Design

1. **Descriptive Names**: Use clear, self-explanatory variable names
2. **Consistent Format**: Use consistent naming conventions
3. **Required vs Optional**: Distinguish between required and optional variables
4. **Default Values**: Consider providing default values for common variables
5. **Validation**: Validate variable inputs where appropriate

## Integration with AI Agents

### Loading System Prompts

```python
# Method 1: Direct loading
system_prompt = load_system_prompt("analyst")
agent = AIAgent("Analyst", broker, system_prompt)

# Method 2: Using loader
loader = PromptLoader()
system_prompt = loader.get_system_prompt("analyst")
agent = AIAgent("Analyst", broker, system_prompt)
```

### Adding Task Templates

```python
# Add task template to agent
template = loader.create_prompt_template("data_analysis", "task")
agent.task_prompts["data_analysis"] = template

# Use in task
task = Task(
    name="Analysis Task",
    data={"prompt_template": "data_analysis", ...}
)
agent.add_task(task)
```

### Dynamic Prompt Updates

```python
# Update system prompt at runtime
new_prompt = loader.get_system_prompt("specialist")
agent.update_system_prompt(new_prompt)

# Add new task template
new_template = loader.create_prompt_template("new_task", "task")
agent.task_prompts["new_task"] = new_template
```

## Examples

See the `/examples/` directory for complete, working examples of prompts with real data and expected outputs.

## Contributing

When adding new prompts:

1. Follow the directory structure conventions
2. Use clear, descriptive names
3. Include variable placeholders where appropriate
4. Add documentation and examples
5. Test prompts with the prompt loader
6. Update this README if adding new categories

## File Format

All prompts are stored as Markdown (`.md`) files for:
- Easy reading and editing
- Version control compatibility
- Support for formatting and structure
- Integration with documentation tools 