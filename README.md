# blablado

`blablado` is an extensible Assistant, that listens to your voice and can execute custom Python functions you provided. 
It can speak as well. It is based on [LangChain](https://python.langchain.com/docs/get_started/introduction.html) and [OpenAI's API](https://openai.com/blog/openai-api). You need an openai API account to use it.

## Usage: API

You can use it from Python ([see example notebook](https://github.com/haesleinhuepf/blablado/blob/main/demo/API_demo.ipynb)) by 

* initializing an `Assistant`, 
```python
from blablado import Assistant
assistant = Assistant()
```

* providing functions/tools and

```python
from datetime import datetime

@assistant.register_tool
def book_room(room:str, author:str, start:datetime, end:datetime):
    """Book a room for a specific person from start to end time."""
    
    print(f"""
    Booking {room} for {author} from {start} to {end}.
    """)
```


* prompting for tasks

```python
assistant.do("Hi I'm Robert, please book room A03.21 for me from 3 to 4 pm tomorrow. Thanks")
```

Output:
```
I have successfully booked room A03.21 for Robert from 3 to 4 pm tomorrow.
```

## Usage: Microphone

You can also use it via microphone ([see example notebook](https://github.com/haesleinhuepf/blablado/blob/main/demo/audio_demo.ipynb)). Therfore, it is recommended to print out the list of available microphones like this:

```python
from blablado import list_microphones
list_microphones()
```
Example output:
```
['Microsoft Sound Mapper - Input',
 'Microphone (KLICK&SHOW Audio)',
 'AI Noise-cancelling Input (ASUS',
 'Headset (MAJOR IV Hands-Free AG',
 'Microphone Array (Realtek(R) Au']
```

Then, choose the right microphone after initializing the assistant:

```python
from blablado import Assistant
assistant = Assistant()
assistant.microphone_index = 3
```

You can then call the assistant to listen to your voice and execute the function you want to call:
```python
assistant.listen()
```

## Usage: Voice output

To make the voice output work as well, just activate the voice when initializing the assistant:

```python
from blablado import Assistant
assistant = Assistant(has_voice=True)
```

## Installation

`blablado` is available on pypi and can be installed using `pip`. It is recommended to install it in a virtual environment, e.g. set up with mamba.

```
mamba create --name bla python=3.9
```

```
mamba activate bla
```

```
pip install blablado
```

To make the voice-output work (optional), consider installing [ffmpeg](https://anaconda.org/conda-forge/ffmpeg) using mamba.

```
mamba install ffmpeg
```

## Issues

If you encounter any problems or want to provide feedback or suggestions, please create a thread on [image.sc](https://image.sc) along with a detailed description and tag [@haesleinhuepf].

## Acknowledgements

Parts of the code reused here were originally written by [kevinyamauchi](https://github.com/kevinyamauchi) for the [bia-bob](https://github.com/haesleinhuepf/bia-bob) project.




