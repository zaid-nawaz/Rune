
from pathlib import Path

from app.video.models import EditingPlan
from app.video.registry import OPERATIONS


def execute_plan(
    input_path: Path,
    output_path: Path,
    plan: EditingPlan,
) -> Path:

    current_input = input_path

    print(f"Input: {input_path}")
    print(f"Final output: {output_path}")
    print(f"Operations: {len(plan.operations)}")
    
    temporary_files = []

    for index, operation in enumerate(plan.operations):

        operation_name = operation.operation
        
        if index == len(plan.operations) - 1:
            current_output = output_path
        else:
            current_output = (
                output_path.parent
                / f".tmp_{index}.mp4"
            )
            
            temporary_files.append(current_output)
            

        current_output.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        print(f"Operation #{index + 1}")
        print(f"Name: {operation_name}")
        print(f"Parameters: {operation.parameters}")
        print(f"Input: {current_input}")
        
        if operation_name == "custom_ffmpeg":

            description = operation.parameters.get(
                "description"
            )

            if not description:
                raise ValueError(
                    "custom_ffmpeg requires a description."
                )

            from app.video.custom_executor import (
                execute_custom_ffmpeg,
            )

            execute_custom_ffmpeg(
                description=description,
                input_path=current_input,
                output_path=current_output,
            )

            current_input = current_output

            continue



        if operation_name not in OPERATIONS:
            raise ValueError(
                f"Unknown operation: {operation_name}"
            )

        operation_function = OPERATIONS[operation_name]



        try:
            operation_function(
                input_path=current_input,
                output_path=current_output,
                **operation.parameters,
            )

        except TypeError as e:
            raise ValueError(
                f"Invalid parameters for operation "
                f"'{operation_name}': {e}"
            ) from e

        if not current_output.exists():
            raise RuntimeError(
                f"Operation '{operation_name}' "
                f"did not create output file: "
                f"{current_output}"
            )

        current_input = current_output

    for temporary_file in temporary_files:
        if temporary_file.exists():
            temporary_file.unlink()

    print(f"Final output: {current_input}")

    return current_input