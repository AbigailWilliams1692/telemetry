#######################################################
# @Project: Telemetry
# @Module: tracer_factory.py
# @Description: This module provides a class for tracing function calls
# @Author: AbigailWilliams1692
# @CreationDate: 2025-07-23
#######################################################

#######################################################
# Import Libraries
#######################################################
# Standard Libraries
import atexit
import logging
import queue
import time
import threading
import types
from functools import wraps
from typing import Callable

# Third-Party Libraries

# Local Libraries
from log import get_logger
from handler import Handler

#######################################################
# Logging Configuration
#######################################################
_logger = get_logger(name=__name__, log_level=logging.INFO)


#######################################################
# Class: TracerFactory
#######################################################
class TracerFactory:
    """
    A class for manufacturing TracerFactory instances that can be used to trace function calls
    """

    ######################################################
    # Default Methods
    ######################################################
    def __init__(self,
                 max_queue_size: int = 1000,
                 flush_interval: int = 5,  # seconds
                 flush_on_exit: bool = True,
                 handlers: list[Handler] = None,
                 log_level: int = logging.INFO
                 ) -> None:
        """
        Constructor for the TracerFactory class.

        :param max_queue_size: Maximum size of the queue for telemetry records.
        :param flush_interval: Interval in seconds to flush the queue.
        :param flush_on_exit: Whether to flush the queue on exit.
        :param handlers: List of Handler instances to export telemetry data.
        :param log_level: Logging level for the tracer.
        :return: None.
        """
        # Fields
        self.max_queue_size = max_queue_size
        self.flush_interval = flush_interval
        self.flush_on_exit = flush_on_exit
        self.handlers = handlers if handlers is not None else []
        self._logger = get_logger(name=__name__, log_level=log_level)

        # Initialize the queue for telemetry records.
        self._queue = queue.Queue(maxsize=self.max_queue_size)
        self._flush_lock = threading.Lock()
        self._flush_thread = None
        self._stop_event = threading.Event()

        # Start a background thread to flush the queue periodically.
        self._start_auto_flush()

        # Register the exit handler to flush the queue on exit if specified.
        if self.flush_on_exit:
            atexit.register(self._on_exit)

    def __call__(self, user_id: str) -> Callable:
        """
        Decorator to trace function calls and log telemetry data.

        :param user_id: Unique identifier for the user.
        :return: Decorated function that traces calls.
        """

        def decorator(func: types.FunctionType) -> Callable:
            """
            Decorator that wraps a function to trace its execution.

            :param func: The function to be traced.
            :return: a wrapped function that logs telemetry data.
            """

            @wraps(func)
            def wrapper(*args, **kwargs):

                # Prepare the telemetry record information
                start_time = time.perf_counter()
                status = "success"
                error_info = ""
                result = None

                try:
                    # Call the original function
                    result = func(*args, **kwargs)
                except Exception as e:
                    # If an exception occurs, log the error and set status to "error"
                    self._logger.error(user_id, func.__name__, e)

                    # Capture the error information
                    status = "error"
                    error_info = str(e)
                    raise
                finally:
                    # Record the end time of the function call
                    end_time = time.perf_counter()
                    elapsed_time = end_time - start_time

                    # Construct the record data
                    record = self._generate_a_record(
                        user_id=user_id,
                        module_name=func.__module__,
                        function_name=func.__name__,
                        elapsed_time=elapsed_time,
                        status=status,
                        error_info=error_info,
                        result=result
                    )

                    # Add the telemetry record to the queue
                    self._add_to_queue(record=record)

                return result

            return wrapper

        return decorator

    def __str__(self) -> str:
        """
        Returns a string representation of the TracerFactory instance.
        """
        return f"TracerFactory<{id(self)}>"

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the TracerFactory instance.
        """
        return self.__str__()

    ######################################################
    # Utility Methods
    ######################################################
    @staticmethod
    def _generate_a_record(user_id: str, module_name: str, function_name: str,
                           elapsed_time: float, status: str,
                           error_info: str = "", result=None) -> dict:
        """
        Generate a telemetry record.

        :param user_id: Unique identifier for the user.
        :param module_name: Name of the module where the function is defined.
        :param function_name: Name of the function being traced.
        :param elapsed_time: Time taken to execute the function.
        :param status: Status of the function call (success or error).
        :param error_info: Error information if an error occurred.
        :param result: Result of the function call.
        :return: A dictionary representing the telemetry record.
        """
        return {
            "user_id": user_id,
            "module_name": module_name,
            "function_name": function_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            "elapsed_time": elapsed_time,
            "status": status,
            "error_info": error_info,
            "result": result
        }

    def _add_to_queue(self, record: dict) -> None:
        """
        Add a telemetry record to the queue.

        :param record: The telemetry record to add.
        :return: None.
        """
        try:
            self._queue.put(record, block=False)
            self._logger.debug(f"Record added to queue: {record}")
        except queue.Full:
            self._logger.warning("Queue is full, dropping record.")
            self.flush()
            self._queue.put(record, block=False)

    def flush(self) -> None:
        """
        Flush the queue and export telemetry records using the registered handlers.

        :return: None.
        """
        with self._flush_lock:
            self._logger.debug("Flushing the queue.")

            # If the queue is empty, log a debug message and return
            if self._queue.empty():
                self._logger.debug("Queue is empty, nothing to flush.")
                return

            # Collect all records from the queue
            records = []
            while not self._queue.empty():
                try:
                    record = self._queue.get(block=False, timeout=1)
                    records.append(record)
                except queue.Empty:
                    break
            self._logger.debug(f"Collected {len(records)} records from the queue.")

            # Save the records using the handlers
            if records:
                self._logger.debug(f"Saving the records.")
                self._save_records(records=records)
            else:
                self._logger.debug("No records to flush.")

    def _save_records(self, records: list[dict]) -> None:
        """
        Save the telemetry records using the registered handlers.

        :param records: List of telemetry records to save.
        :return: None.
        """
        for handler in self.handlers:
            try:
                handler.export(records=records)
                self._logger.info(f"Records exported successfully using {handler}.")
            except NotImplementedError as e:
                self._logger.error(f"Handler {handler} has not implemented export method: {e}")
            except Exception as e:
                self._logger.error(f"Failed to export records using {handler}: {e}")

    def _auto_flush_loop(self) -> None:
        """
        Background thread loop to flush the queue at regular intervals.

        :return: None.
        """
        while not self._stop_event.is_set():
            # Wait for the flush interval
            self._stop_event.wait(timeout=self.flush_interval)

            # Check if to exit
            if self._stop_event.is_set():
                self._logger.debug("Auto Flushing Loop stopped.")
                break

            # Flush
            try:
                self.flush()
            except Exception as e:
                self._logger.error(f"Auto Flushing failed: {str(e)}")
                raise

    def _start_auto_flush(self) -> None:
        """
        Start the background thread for auto-flushing the queue.

        :return: None.
        """
        if self._flush_thread is None or not self._flush_thread.is_alive():
            self._flush_thread = threading.Thread(target=self._auto_flush_loop, daemon=True)
            self._flush_thread.start()
            self._logger.debug("Auto Flushing Loop started.")
        else:
            self._logger.debug("Auto Flushing Loop is already running.")

    def _on_exit(self) -> None:
        """
        Exit handler to flush the queue when the program exits.

        :return: None.
        """
        # Log the exit event
        self._logger.info("Exiting TracerFactory, flushing the queue for one last time.")

        # Flush the queue one last time before exiting
        self.flush()

        # Stop the auto-flush thread
        self._stop_event.set()
        if self._flush_thread is not None:
            self._flush_thread.join()
            self._logger.debug("Auto Flushing Loop has been stopped.")

    def add_handler(self, handler: Handler) -> None:
        """
        Add a handler to the TracerFactory.

        :param handler: An instance of Handler to add.
        :return: None.
        """
        if isinstance(handler, Handler):
            self.handlers.append(handler)
            self._logger.info(f"Handler {handler} added successfully.")
        else:
            self._logger.error("The provided handler is not an instance of Handler.")
            raise TypeError("Handler must be an instance of Handler class.")

    ######################################################
    # Methods: Metadata and Stats
    ######################################################
    def get_metadata(self) -> dict:
        """
        Get metadata about the TracerFactory instance.

        :return: A dictionary containing metadata.
        """
        return {
            "id": id(self),
            "max_queue_size": self.max_queue_size,
            "flush_interval": self.flush_interval,
            "flush_on_exit": self.flush_on_exit,
            "handlers_count": len(self.handlers),
            "queue_size": self._queue.qsize(),
            "flush_thread_alive": self._flush_thread.is_alive() if self._flush_thread else False
        }
