import numpy as np
import cohere
from decouple import config

co = cohere.ClientV2(api_key=config("COHERE_API_KEY", cast=str, default=""))
