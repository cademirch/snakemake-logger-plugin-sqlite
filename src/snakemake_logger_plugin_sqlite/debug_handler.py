# src/snakemake_logger_plugin_sqlite/handler.py
import logging
from rich.console import Console
from rich.pretty import pprint
from snakemake_interface_logger_plugins.common import LogEvent

# Import parsers
from snakemake_logger_plugin_sqlite.parsers import (
    WorkflowStarted,
    JobInfo,
    JobStarted,
    JobFinished,
    ShellCmd,
    JobError,
    GroupInfo,
    GroupError,
    ResourcesInfo,
    DebugDag,
    Progress,
    RuleGraph,
    RunInfo,
)


class DebugHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.console = Console()

        # Map event types to their corresponding parser classes
        self.parsers = {
            LogEvent.WORKFLOW_STARTED.value: WorkflowStarted,
            LogEvent.JOB_INFO.value: JobInfo,
            LogEvent.JOB_STARTED.value: JobStarted,
            LogEvent.JOB_FINISHED.value: JobFinished,
            LogEvent.SHELLCMD.value: ShellCmd,
            LogEvent.JOB_ERROR.value: JobError,
            LogEvent.GROUP_INFO.value: GroupInfo,
            LogEvent.GROUP_ERROR.value: GroupError,
            LogEvent.RESOURCES_INFO.value: ResourcesInfo,
            LogEvent.DEBUG_DAG.value: DebugDag,
            LogEvent.PROGRESS.value: Progress,
            LogEvent.RULEGRAPH.value: RuleGraph,
            LogEvent.RUN_INFO.value: RunInfo,
        }

    def emit(self, record: logging.LogRecord) -> None:
        # Get the event type
        event = getattr(record, "event", record.levelname)

        try:
            # Try to get a proper LogEvent value
            if isinstance(event, str):
                event_value = event.lower()
                log_event = LogEvent(event_value)
            else:
                log_event = event
                event_value = log_event.value

            rule_title = f"Log Record: {log_event.value}"
        except ValueError:
            # Fallback for unknown event types
            event_value = str(event).lower()
            rule_title = f"Unknown Event: {event_value}"

        # Get the raw record data for comparison
        record_simplified = {
            "message": record.msg,
            "extra": {
                k: v
                for k, v in record.__dict__.items()
                if k
                not in [
                    "msg",
                    "args",
                    "exc_info",
                    "exc_text",
                    "pathname",
                    "lineno",
                    "filename",
                    "module",
                    "name",
                    "levelno",
                    "levelname",
                    "funcName",
                    "created",
                    "asctime",
                    "msecs",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "processName",
                    "process",
                ]
            },
        }

        # Try to parse the record with the appropriate parser
        parsed_data = None
        parser_class = self.parsers.get(event_value)

        if parser_class:
            try:
                parsed_data = parser_class.from_record(record)
            except Exception as e:
                parsed_data = f"Parsing error: {str(e)}"

        # Display the results
        self.console.rule(rule_title)

        # Show original record for comparison
        self.console.print("[bold]Original Record:[/bold]")
        pprint(record_simplified, expand_all=True)

        # Show parsed data if available
        if parsed_data:
            self.console.print("\n[bold]Parsed Data:[/bold]")
            pprint(parsed_data, expand_all=True)

            # # Also show the model dump for a clean view
            # self.console.print("\n[bold]Model as Dict:[/bold]")
            # if hasattr(parsed_data, "model_dump"):
            #     pprint(parsed_data.model_dump(), expand_all=True)
            # else:
            #     self.console.print("Could not convert to dict")
        else:
            self.console.print("\n[bold]No parser available for this event type[/bold]")

        self.console.rule()
