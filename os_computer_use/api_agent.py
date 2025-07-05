from os_computer_use.sandbox_agent import SandboxAgent as BaseSandboxAgent
from os_computer_use.config import vision_model, action_model, grounding_model
from os_computer_use.llm_provider import Message
from os_computer_use.logging import logger
import json
from datetime import datetime


class APISandboxAgent(BaseSandboxAgent):
    """
    Enhanced SandboxAgent for API usage with single-step execution capability
    """

    def __init__(self, sandbox, output_dir=".", save_logs=True):
        super().__init__(sandbox, output_dir, save_logs)
        self.tracked_actions = []

    def execute_single_step(self, instruction):
        """
        Execute a single step towards completing the instruction
        Returns the action taken and whether the task is complete
        """
        try:
            # Add the instruction to messages if it's new
            if (
                not self.messages
                or self.messages[-1].get("content") != f"OBJECTIVE: {instruction}"
            ):
                self.messages.append(Message(f"OBJECTIVE: {instruction}"))
                logger.log(f"USER: {instruction}", print=False)

            # Stop the sandbox from timing out - increase to 30 minutes
            self.sandbox.set_timeout(1800)

            # Get the current thought and action
            content, tool_calls = action_model.call(
                [
                    Message(
                        "You are an AI assistant with computer use abilities.",
                        role="system",
                    ),
                    *self.messages,
                    Message(
                        logger.log(f"THOUGHT: {self.append_screenshot()}", "green")
                    ),
                    Message(
                        "I will now use tool calls to take the next single action, or use the stop command if the objective is complete.",
                    ),
                ],
                self.get_tools(),
            )

            if content:
                self.messages.append(Message(logger.log(f"THOUGHT: {content}", "blue")))

            # Execute the first tool call only (single step)
            if tool_calls:
                tool_call = tool_calls[0]  # Take only the first action
                name, parameters = tool_call.get("name"), tool_call.get("parameters")

                # Check if task is complete
                completed = name == "stop"

                if not completed:
                    # Execute the action
                    logger.log(f"ACTION: {name} {str(parameters)}", "red")
                    self.messages.append(Message(json.dumps(tool_call)))
                    result = self.call_function(name, parameters)
                    self.messages.append(
                        Message(logger.log(f"OBSERVATION: {result}", "yellow"))
                    )

                    return {
                        "action": name,
                        "parameters": parameters,
                        "result": result,
                        "completed": False,
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "action": "stop",
                        "parameters": {},
                        "result": "Task completed",
                        "completed": True,
                        "timestamp": datetime.now().isoformat(),
                    }
            else:
                # No actions returned, might be an error or completion
                return {
                    "action": "none",
                    "parameters": {},
                    "result": "No action determined",
                    "completed": False,
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            return {
                "action": "error",
                "parameters": {},
                "result": f"Error: {str(e)}",
                "completed": False,
                "timestamp": datetime.now().isoformat(),
            }

    def get_tools(self):
        """Get the available tools"""
        from os_computer_use.sandbox_agent import tools

        return tools

    def run_with_tracking(self, instruction):
        """
        Run the agent with action tracking for API usage
        """
        self.tracked_actions = []
        completed = False
        stop_detected = False
        max_iterations = 20  # Prevent infinite loops
        iteration_count = 0

        # Override call_function to track actions and detect completion
        original_call_function = self.call_function

        def tracked_call_function(name, arguments):
            nonlocal stop_detected
            result = original_call_function(name, arguments)

            action_data = {
                "action": name,
                "parameters": arguments,
                "result": result,
                "timestamp": datetime.now().isoformat(),
            }

            # Check if this is a stop action
            if name == "stop":
                stop_detected = True
                action_data["completed"] = True

            self.tracked_actions.append(action_data)
            return result

        self.call_function = tracked_call_function

        try:
            # Add the instruction to messages
            self.messages.append(Message(f"OBJECTIVE: {instruction}"))
            logger.log(f"USER: {instruction}", print=False)

            should_continue = True
            while should_continue and iteration_count < max_iterations:
                iteration_count += 1

                # Stop the sandbox from timing out - increase to 30 minutes
                self.sandbox.set_timeout(1800)

                content, tool_calls = action_model.call(
                    [
                        Message(
                            "You are an AI assistant with computer use abilities.",
                            role="system",
                        ),
                        *self.messages,
                        Message(
                            logger.log(f"THOUGHT: {self.append_screenshot()}", "green")
                        ),
                        Message(
                            "I will now use tool calls to take these actions, or use the stop command if the objective is complete.",
                        ),
                    ],
                    self.get_tools(),
                )

                if content:
                    self.messages.append(
                        Message(logger.log(f"THOUGHT: {content}", "blue"))
                    )

                should_continue = False
                for tool_call in tool_calls:
                    name, parameters = tool_call.get("name"), tool_call.get(
                        "parameters"
                    )
                    should_continue = name != "stop"
                    if not should_continue:
                        stop_detected = True
                        break
                    # Print the tool-call in an easily readable format
                    logger.log(f"ACTION: {name} {str(parameters)}", "red")
                    # Write the tool-call to the message history using the same format used by the model
                    self.messages.append(Message(json.dumps(tool_call)))
                    result = self.call_function(name, parameters)

                    self.messages.append(
                        Message(logger.log(f"OBSERVATION: {result}", "yellow"))
                    )

            # Determine completion status
            completed = stop_detected

            # If we hit max iterations without stop, mark as incomplete
            if iteration_count >= max_iterations and not stop_detected:
                self.tracked_actions.append(
                    {
                        "action": "timeout",
                        "parameters": {"max_iterations": max_iterations},
                        "result": f"Task stopped after {max_iterations} iterations without completion",
                        "timestamp": datetime.now().isoformat(),
                        "completed": False,
                    }
                )

        except Exception as e:
            completed = False
            self.tracked_actions.append(
                {
                    "action": "error",
                    "parameters": {},
                    "result": str(e),
                    "timestamp": datetime.now().isoformat(),
                    "completed": False,
                }
            )
        finally:
            # Restore original function
            self.call_function = original_call_function

        return self.tracked_actions, completed
