from fastapi import FastAPI, HTTPException
from backend.github_service import get_user_repos
from backend.analyzer import analyze_repos, generate_suggestions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DevTrack AI",
    description="Analyze GitHub profiles and generate improvement suggestions",
    version="1.0.0"
)

# CORS (for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to your frontend URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check (important for deployment platforms)
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Server is running"}

# ✅ Main API
@app.get("/user/{username}")
def get_user(username: str):
    try:
        repos = get_user_repos(username)

        if not repos:
            raise HTTPException(
                status_code=404,
                detail="User not found or no public repositories"
            )

        analysis = analyze_repos(repos)

        suggestions = generate_suggestions(
            analysis.get("total_repos", 0),
            analysis.get("total_stars", 0),
            analysis.get("languages_used", [])
        )

        return {
            "success": True,
            "data": {
                "username": username,
                "avatar": repos[0]["owner"]["avatar_url"],
                "profile": repos[0]["owner"]["html_url"],
                "analysis": analysis,
                "suggestions": suggestions
            }
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )