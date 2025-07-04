from pathlib import Path
import numpy as np
import cohere
from environ import Env

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env(BASE_DIR / ".env")

co = cohere.ClientV2(api_key=env("COHERE_API_KEY", default=""))
