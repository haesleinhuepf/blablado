class Assistant():
    """
    An Assistant is an object that holds a list of tools, that can be extended, and functions for receiving
    instructions, either as string or as input from a microphone. The Assistant can then execute the given command
    by using the tools. Tools are callable functions that can be registered with the assistant.
    """
    def __init__(self, temperature=0.01, tools=[], verbose=False, has_voice=False):
        self._tools = tools
        self._has_voice = has_voice
        self._verbose = verbose
        self._microphone_index = None
        self._microphone_timeout = 10 # seconds

        if self._verbose:
            print("Initializing assistant...")

        if len(self._tools) == 0:
            self.register_tool(self.list_tools)

        self._temperature = temperature

    def _initialize_agent(self):
        """
        Initializes the agent/llm/memory with a given list of tools. Wheneve a tool is added, we neeed to
        reinititalize the agent.
        """
        from langchain.chat_models import ChatOpenAI
        from langchain.memory import ConversationBufferMemory
        from langchain.agents import StructuredChatAgent, AgentExecutor, OpenAIFunctionsAgent, initialize_agent, \
            AgentType
        from langchain.prompts import MessagesPlaceholder
        from langchain.schema import SystemMessage

        # make the llm
        self._llm = ChatOpenAI(temperature=self._temperature)

        # set up the chat memory
        MEMORY_KEY = "chat_history"
        self._memory = ConversationBufferMemory(memory_key=MEMORY_KEY, return_messages=True)

        system_message = SystemMessage(content="""
        Answer the human's questions below and keep your answers short.
        Be honest. Never lie. 
        Only say you did something, if a function/tool has been called that can actually do the task you were asked for.
        """)
        agent_kwargs = {
            "system_message": system_message,
            "extra_prompt_messages": [MessagesPlaceholder(variable_name=MEMORY_KEY)]
        }
        self._agent = initialize_agent(
            self._tools,
            self._llm,
            agent=AgentType.OPENAI_FUNCTIONS,
            verbose=self._verbose,
            agent_kwargs=agent_kwargs,
            memory=self._memory,
        )

    def list_tools(self):
        """Lists all available tools"""
        return "\n".join(list([t.name for t in self._tools]))

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

    def do(self, prompt: str = None):
        from ._speak import speak_out
        from datetime import datetime

        if self._agent is None:
            self._initialize_agent()

        if self._verbose:
            print("Tools:", len(self._tools))

        now = datetime.now()

        # why? https://github.com/haesleinhuepf/bia-bob/issues/13
        if not prompt.strip().endswith("?"):
            prompt = prompt + "\nSummarize the answers in maximum two sentences."


        prompt = f"""
The current date and time are {now}.

{prompt}
"""


        result = self._agent.run(input=prompt)

        print(result)
        if self._has_voice:
            speak_out(result)

    def register_tool(self, func):
        """
        Adds a function tool to the agent.

        The given callable must have parameters of type string, int and float.
        It must have a docstring that describes the function, ideally explaining what the function is useful for using
        terms from the target audience.

        After calling this function, the agent is re-initialized.
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
    def has_voice(self):
        return self._has_voice

    @has_voice.setter
    def has_voice(self, has_voice:bool):
        """
        Turn on/off voice output
        """
        self._has_voice = has_voice

