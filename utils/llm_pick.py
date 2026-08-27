from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


def pick_llm(level : str):
    """
    Picks the appropriate LLM based on the level of the question.

    Args:
        level (str): The level of the question, can be "easy", "medium", or "hard".

    Returns:
        str: The name of the LLM to be used.
    """

    if level.lower() == "low":
        llm = ChatGroq(model_name="openai/gpt-oss-20b", temperature = 0)
    elif level.lower() == "medium":
        llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature = 0)
    elif level.lower() == "high":
        llm = ChatGroq(model_name="openai/gpt-oss-120b", temperature = 0)
    else:
        raise ValueError(f"Unsupported level: {level}")

    return llm 


# This if loop runs only when we run this file and if we import this file in any other file
# then this if loop will not run. This is a good practice to test the functionality of the code
#  in the file.
if __name__ == "__main__":
    llm_obj = pick_llm("low")
    print(llm_obj.invoke("What is the capital of France?"))