from backend.utils.gemini import Gemini
def generate(scheme_name: str = None, query: str = None) -> dict:
    scheme=scheme_name or query
    gemini = Gemini()
    res=gemini.generate(scheme_name=scheme)
    return res
