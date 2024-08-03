


class Assistant():
    """
    An Assistant is an object that holds a list of tools, that can be extended, and functions for receiving
    instructions, either as string or as input from a microphone. The Assistant can then execute the given command
    by using the tools. Tools are callable functions that can be registered with the assistant.
    """
    def __init__(self, temperature=0.01, tools=[], verbose=False, voice=None, model="gpt-4o-2024-05-13", base_url:str=None, api_key:str=None):
        self._tools = tools
        self.voice = voice
        self._verbose = verbose
        self._microphone_index = None
        self._microphone_timeout = 10 # seconds
        self._model = model
        self._agent = None
        if base_url == 'ollama':
            base_url = 'http://localhost:11434/v1'
        self._base_url = base_url
        self._api_key = api_key

        if self._verbose:
            print("Initializing assistant...")

        if len(self._tools) == 0:
            self.register_tool(self.list_tools)
            self.register_tool(self.change_voice)

        self._temperature = temperature

    def _initialize_agent(self):
        """
        Initializes the agent/llm/memory with a given list of tools. Whenever a tool is added, we neeed to
        reinititalize the agent.
        """
        from langchain_openai import ChatOpenAI
        from langchain.agents import create_openai_functions_agent
        from langchain.agents.openai_functions_multi_agent.base import OpenAIMultiFunctionsAgent
        from langchain.prompts import MessagesPlaceholder
        from langchain_core.messages import SystemMessage
        from langchain.memory import ConversationBufferMemory
        from langchain.agents import OpenAIFunctionsAgent, AgentExecutor
        import os

        # Assuming you have a language model and tools
        #llm = ChatOpenAI(temperature=self._temperature, model=self._model)
        if self._base_url is not None:
            llm = ChatOpenAI(temperature=self._temperature,
                             openai_api_key = self._api_key,
                             openai_api_base = self._base_url,
                             model = self._model
                             )
        else:
            llm = ChatOpenAI(temperature=self._temperature, model=self._model)

        # Create a custom system message
        custom_system_message = SystemMessage(content="""
                Answer the human's questions below and keep your answers as short as possible.
                Be honest. Never lie. 
                Only say you did something, if a function/tool has been called that can actually do the task you were asked for.
                """)

        # Create the agent
        self._agent = OpenAIMultiFunctionsAgent.from_llm_and_tools(
            llm,
            self._tools,
            extra_prompt_messages=[custom_system_message],
        )


        memory = ConversationBufferMemory(
            llm=llm,
            memory_key="memory",
            return_messages=True)

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=custom_system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="memory")],
        )

        agent = create_openai_functions_agent(llm=llm, tools=self._tools, prompt=prompt)

        self._agent = AgentExecutor(
            agent=agent,
            tools=self._tools,
            memory=memory,
            verbose=self._verbose,
            return_intermediate_steps=False,
            handle_parsing_errors=True
        )

    def list_tools(self):
        """Lists all available tools"""
        return "\n".join(list([t.name for t in self._tools]))

    def change_voice(self, voice:str):
        """
        Change the voice used for speaking out. Voice must be one of "alloy", "echo", "fable", "onyx", "nova", "shimmer", "google", "silent".
        """
        self._voice = voice if voice != "silent" else None

    def listen(self, until_bye_bye=False):
        """
        Activate the microphone and listen to the user.
        The passed command is then executed.

        If until_bye_bye is True, the discussion is continued until the user says "bye bye".
        """
        from ._speech_recognition import listen_to_microphone

        while True:
            result = listen_to_microphone(self._microphone_index, timeout=self._microphone_timeout)
            if result:
                self.do(result)

                if result.lower().strip() in ["bye bye", "bye-bye", "bye", "goodbye", "good bye", "good-bye",
                                              "see you later", "see you", "stop", "quit", "halt"]:
                    return

            else:
                return

            if not until_bye_bye:
                return

    def discuss(self):
        """Have a continuous discussion with the assistant until we say bye bye."""
        return self.listen(until_bye_bye=True)

    def do(self, prompt: str = None):
        from ._speak import speak_out

        result = self.tell(prompt)

        if is_notebook():
            from IPython.display import display, Markdown
            display(Markdown(result))
        else:
            print(result)
        if self._voice is not None:
            speak_out(result, voice=self._voice)

    def tell(self, prompt:str = None):
        from datetime import datetime
        now = datetime.now()

        if self._agent is None:
            self._initialize_agent()

        if self._verbose:
            print("Tools:", len(self._tools))

        prompt = f"""
Here are some general information, no need to mention it unless asked for it:
* The current date and time are {now}.

This is your task:
{prompt}
"""

        return self._agent.invoke({"input": prompt})['output']


    def register_tool(self, func):
        """
        Adds a function tool to the agent.

        The given callable must have parameters of type string, int and float.
        It must have a docstring that describes the function, ideally explaining what the function is useful for using
        terms from the target audience.

        After calling this function, the agent must be re-initialized.
        """
        from langchain.tools import StructuredTool

        self._tools.append(StructuredTool.from_function(func))

        self._agent = None

    @property
    def microphone_index(self):
        return self._microphone_index

    @microphone_index.setter
    def microphone_index(self, index:int):
        self._microphone_index = index

    @property
    def microphone_timeout(self):
        return self._microphone_timeout

    @microphone_timeout.setter
    def microphone_timeout(self, timeout:int):
        self._microphone_timeout = timeout

    @property
    def voice(self):
        return self._voice

    @voice.setter
    def voice(self, voice:str):
        """
        Switch to a different voice. Voice must be one of "alloy", "echo", "fable", "onyx", "nova", "shimmer", "google", "silent".
        """
        if voice == True:
            voice = "nova"
        if voice == False:
            voice = None
        self._voice = voice

def is_notebook() -> bool:
    """Returns true if the code is currently executed in a Jupyter notebook."""
    # adapted from: https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
    try:
        from IPython.core.getipython import get_ipython

        try:
            shell = get_ipython().__class__.__name__
            if shell == 'ZMQInteractiveShell':
                return True  # Jupyter notebook or qtconsole
            elif shell == 'TerminalInteractiveShell':
                return False  # Terminal running IPython
            else:
                return False  # Other type (?)
        except NameError:
            return False  # Probably standard Python interpreter
    except:
        return False # importing IPython failed
