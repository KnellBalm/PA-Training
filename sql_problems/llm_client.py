import os
import google.generativeai as genai  # pip install google-generativeai

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("환경변수 GEMINI_API_KEY가 설정되어 있지 않습니다.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-pro")  # 모델명은 필요시 수정
