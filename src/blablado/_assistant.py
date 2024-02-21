from langchain_core.messages import SystemMessage


class Assistant():
    """
    An Assistant is an object that holds a list of tools, that can be extended, and functions for receiving
    instructions, either as string or as input from a microphone. The Assistant can then execute the given command
    by using the tools. Tools are callable functions that can be registered with the assistant.
    """
    def __init__(self, temperature=0.01, tools=[], verbose=False, has_voice=False, model="gpt-3.5-turbo-0613"):
        self._tools = tools
        self._has_voice = has_voice
        self._verbose = verbose
        self._microphone_index = None
        self._microphone_timeout = 10 # seconds
        self._model = "gpt-3.5-turbo-0613"

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
        from langchain_openai import ChatOpenAI
        from langchain.chains import LLMMathChain
        from langchain.llms import OpenAI
        from langchain.utilities import SerpAPIWrapper, SQLDatabase
        from langchain.agents import Tool, AgentType, create_openai_functions_agent
        from langchain.agents.openai_functions_multi_agent.base import OpenAIMultiFunctionsAgent
        from langchain.prompts import MessagesPlaceholder

        from langchain.memory import ConversationBufferMemory
        from langchain.agents import OpenAIFunctionsAgent, AgentExecutor

        # Assuming you have a language model and tools
        llm = ChatOpenAI(temperature=self._temperature, model=self._model)

        # Create a custom system message
        custom_system_message = SystemMessage(content="""
                Answer the human's questions below and keep your answers short.
                Be honest. Never lie. 
                Only say you did something, if a function/tool has been called that can actually do the task you were asked for.
                """)

        # Create the agent
        self._agent = OpenAIMultiFunctionsAgent.from_llm_and_tools(
            llm,
            self._tools,
            extra_prompt_messages=[custom_system_message],
        )

        llm = ChatOpenAI()

        memory = ConversationBufferMemory(
            llm=llm,
            memory_key="memory",
            return_messages=True)

        prompt = OpenAIFunctionsAgent.create_prompt(
            system_message=custom_system_message,
            extra_prompt_messages=[MessagesPlaceholder(variable_name="memory")],
        )

        #agent = OpenAIFunctionsAgent(llm=llm, tools=self._tools, prompt=prompt)
        agent = create_openai_functions_agent(llm=llm, tools=self._tools, prompt=prompt)

        self._agent = AgentExecutor(
            agent=agent,
            tools=self._tools,
            memory=memory,
            verbose=self._verbose,
            return_intermediate_steps=False,
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
Here are some general information, no need to mention it unless asked for it:
* The current date and time are {now}.

This is your task:
{prompt}
"""

        #result = self._agent.run(prompt)
        result = self._agent.invoke({"input": prompt})['output']

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

