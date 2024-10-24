from dotenv import load_dotenv

if not load_dotenv("test.env", override=True):
    if not load_dotenv("env/test.env", override=True):
        if not load_dotenv("../env/test.env", override=True):
            raise OSError("Unable to locate env file.")
