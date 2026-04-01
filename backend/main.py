from fastapi import FastAPI
from backend.github_service import get_user_repos
from backend.analyzer import analyze_repos, generate_suggestions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Server is working"}

@app.get("/user/{username}")
def get_user(username: str):
    repos = get_user_repos(username)

    if repos is None or len(repos) == 0:
        return {"error": "User not found or no public repositories"}

    analysis = analyze_repos(repos)

    suggestions = generate_suggestions(
        analysis["total_repos"],
        analysis["total_stars"],
        analysis["languages_used"]
    )

    return {
        "username": username,
        "avatar": repos[0]["owner"]["avatar_url"],
        "profile": repos[0]["owner"]["html_url"],
        "analysis": analysis,
        "suggestions": suggestions
    }