"""
Mermaid diagram generation for pipeline visualization.

From Listing 3.5 in Black Hat AI.

Generates Mermaid flowchart syntax for pipeline structure and execution.
"""

from typing import List, Any, Optional
import os


def export_mermaid(stages: List[Any]) -> None:
    """
    Print a Mermaid flowchart of the pipeline stages.

    From Listing 3.5 in Black Hat AI.

    Generates and prints a Mermaid flowchart LR (left-to-right) diagram
    showing the flow between pipeline stages.

    Args:
        stages: List of pipeline stages (must have 'name' attribute)

    Example:
        export_mermaid([recon_agent, triage_agent, report_agent])

        # Output:
        # flowchart LR
        #     recon --> triage
        #     triage --> report
        #     report --> END
    """
    diagram = generate_mermaid(stages)
    print(diagram)


def generate_mermaid(
    stages: List[Any],
    include_status: bool = False,
    stage_status: Optional[dict] = None,
) -> str:
    """
    Generate a Mermaid flowchart diagram string.

    Args:
        stages: List of pipeline stages (must have 'name' attribute)
        include_status: Whether to include status indicators
        stage_status: Optional dict mapping stage names to status

    Returns:
        Mermaid diagram string

    Example:
        diagram = generate_mermaid([recon, triage, report])
        # Save to file or render in markdown
    """
    if not stages:
        return "flowchart LR\n    START --> END"

    lines = ["flowchart LR"]

    for i, stage in enumerate(stages):
        # Get stage name
        name = getattr(stage, "name", str(stage))

        # Get next stage name
        if i + 1 < len(stages):
            next_name = getattr(stages[i + 1], "name", str(stages[i + 1]))
        else:
            next_name = "END"

        # Format node names (capitalize for readability)
        display_name = name.capitalize()
        next_display = next_name.capitalize() if next_name != "END" else "END"

        # Add status styling if requested
        if include_status and stage_status:
            status = stage_status.get(name, "pending")
            if status == "completed":
                lines.append(f"    {name}[{display_name}]:::completed --> {next_name}")
            elif status == "failed":
                lines.append(f"    {name}[{display_name}]:::failed --> {next_name}")
            elif status == "running":
                lines.append(f"    {name}[{display_name}]:::running --> {next_name}")
            else:
                lines.append(f"    {name}[{display_name}] --> {next_name}")
        else:
            lines.append(f"    {name}[{display_name}] --> {next_name}")

    # Add style definitions if using status
    if include_status:
        lines.append("")
        lines.append("    classDef completed fill:#90EE90,stroke:#228B22")
        lines.append("    classDef failed fill:#FFB6C1,stroke:#DC143C")
        lines.append("    classDef running fill:#87CEEB,stroke:#4682B4")

    return "\n".join(lines)


def save_mermaid(
    stages: List[Any],
    output_path: str,
    include_status: bool = False,
    stage_status: Optional[dict] = None,
) -> str:
    """
    Save a Mermaid diagram to a file.

    Args:
        stages: List of pipeline stages
        output_path: Path to save the .mmd file
        include_status: Whether to include status indicators
        stage_status: Optional status mapping

    Returns:
        Path to the saved file
    """
    diagram = generate_mermaid(stages, include_status, stage_status)

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(diagram)

    return output_path


def generate_execution_diagram(
    stages: List[Any],
    artifacts: List[dict],
) -> str:
    """
    Generate a Mermaid diagram with execution status from artifacts.

    Args:
        stages: List of pipeline stages
        artifacts: List of artifact dictionaries with stage and success keys

    Returns:
        Mermaid diagram string with status coloring
    """
    # Build status map from artifacts
    stage_status = {}
    for artifact in artifacts:
        stage_name = artifact.get("stage", "")
        if artifact.get("success"):
            stage_status[stage_name] = "completed"
        else:
            stage_status[stage_name] = "failed"

    return generate_mermaid(stages, include_status=True, stage_status=stage_status)


def generate_sequence_diagram(stages: List[Any]) -> str:
    """
    Generate a Mermaid sequence diagram showing data flow.

    Args:
        stages: List of pipeline stages

    Returns:
        Mermaid sequence diagram string
    """
    if not stages:
        return "sequenceDiagram\n    Note over User: No stages"

    lines = ["sequenceDiagram"]
    lines.append("    participant O as Orchestrator")

    # Add participants
    for stage in stages:
        name = getattr(stage, "name", str(stage))
        lines.append(f"    participant {name} as {name.capitalize()}")

    lines.append("")

    # Add interactions
    prev_name = None
    for stage in stages:
        name = getattr(stage, "name", str(stage))

        if prev_name:
            lines.append(f"    {prev_name}->>O: artifact")
            lines.append(f"    O->>+{name}: run(artifact)")
        else:
            lines.append(f"    O->>+{name}: run(None)")

        lines.append(f"    {name}-->>-O: artifact")
        prev_name = name

    lines.append(f"    Note over O: Pipeline complete")

    return "\n".join(lines)
