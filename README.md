## Conceptual

### Agent

The agent is implemented as a finite state machine (FSM).

The FSM is triggered manually (e.g. by a metrics alert) and runs to completion. 

The states represent steps taken by the algorithm to:
- detect the issue
- plan for a solution
- assign resources to execute the plan
- validate the solution
- reschedule, if necessary to cover for cascading failures

### Flow

The FSM represents the following flow

```mermaid
flowchart TD
    %% --- STYLING ---
    classDef python fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000;
    classDef tool fill:#ffe0b2,stroke:#e65100,stroke-width:2px,stroke-dasharray: 5 5,color:#000;
    classDef llm fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000;
    classDef term fill:#000,stroke:#fff,color:#fff;

    %% --- NODES ---
    Start((START)):::term
    End((END)):::term

    subgraph INIT_PHASE [State: INIT]
        InitAction[Reset Memory]:::python
    end

    subgraph DETECTION_PHASE [State: FAILURE_DETECTION]
        CallDetect1[[Tool: detect_failure_nodes]]:::tool
        CheckFailures{Failures Found?}:::python
    end

    subgraph ANALYSIS_PHASE [State: IMPACT_ANALYSIS]
        CallImpact[[Tool: estimate_impact]]:::tool
        LogImpact[Log Severity to Memory]:::python
    end

    subgraph PLANNING_PHASE [State: REPAIR_PLANNING]
        ContextBuild[Build Prompt with Context]:::python
        CallLLM{{LLM: Query Plan}}:::llm
        ParseJSON[Parse JSON Response]:::python
        CheckValid{Valid Action?}:::python
    end

    subgraph EXEC_PHASE [State: EXECUTION]
        CallAction[[Tool: assign_repair_crew]]:::tool
        StoreResult[Store Result in Memory]:::python
    end

    subgraph FEEDBACK_PHASE [State: RESCHEDULING]
        CallDetect2[[Tool: detect_failure_nodes]]:::tool
        CheckCascade{New Failures?}:::python
    end

    %% --- FLOW ---
    Start --> InitAction
    InitAction --> CallDetect1
    
    CallDetect1 --> CheckFailures
    CheckFailures -- No (Healthy) --> End
    CheckFailures -- Yes (System Broken) --> CallImpact
    
    CallImpact --> LogImpact
    LogImpact --> ContextBuild
    
    ContextBuild --> CallLLM
    CallLLM --> ParseJSON
    ParseJSON --> CheckValid
    
    CheckValid -- Invalid/Error --> ContextBuild
    CheckValid -- Valid Action --> CallAction
    
    CallAction --> StoreResult
    StoreResult --> CallDetect2
    
    CallDetect2 --> CheckCascade
    CheckCascade -- No (Stable) --> End
    CheckCascade -- Yes (Cascading Failure!) --> CallDetect1
    
    %% Add label to the feedback loop
    linkStyle 16 stroke:red,stroke-width:3px,color:red;
```

## Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager

### Installing uv

#### Mac/Linux

```bash
# Install uv using the official installer
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Alternatively, you can use Homebrew on macOS:

```bash
brew install uv
```

#### Windows

Using PowerShell:

```powershell
# Install uv using the official installer
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Alternatively, you can use `pip`:

```powershell
pip install uv
```

### Project Setup

#### Mac/Linux

```bash
# Clone the repository (if not already done)
cd /path/to/project

# Create a virtual environment and install dependencies
uv sync

# Activate the virtual environment (this step might be redundant)
source .venv/bin/activate
```

#### Windows

```powershell
# Clone the repository (if not already done)
cd C:\path\to\project

# Create a virtual environment and install dependencies
uv sync

# Activate the virtual environment (this step might be redundant)
.venv\Scripts\activate
```

### Running the project

Once the virtual environment is activated, you can run the project:

#### Run the main application

```bash
uv run python -m infra_fail_mngr.main
```

#### Run all tests

```bash
uv run pytest
```

