from fastapi import FastAPI, HTTPException
from backend.github_service import get_user_repos
from backend.analyzer import analyze_repos, generate_suggestions
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import httpx
import os

# 🔐 Use environment variables (IMPORTANT)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

app = FastAPI(
    title="DevTrack AI",
    description="Analyze GitHub profiles and generate improvement suggestions",
    version="1.0.0"
)

# 🌐 CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Server is running"}


# 🔐 GitHub Login Route
@app.get("/auth/github")
def github_login():
    if not CLIENT_ID:
        raise HTTPException(status_code=500, detail="CLIENT_ID not set")

    github_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
    return RedirectResponse(github_url)


# 🔐 GitHub Callback Route
@app.get("/auth/github/callback")
async def github_callback(code: str):
    try:
        async with httpx.AsyncClient() as client:
            token_res = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "code": code
                }
            )

        token_json = token_res.json()
        access_token = token_json.get("access_token")

        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to get access token")

        async with httpx.AsyncClient() as client:
            user_res = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"token {access_token}"}
            )

        user_data = user_res.json()

        return {
            "success": True,
            "data": {
                "username": user_data.get("login"),
                "avatar": user_data.get("avatar_url"),
                "profile": user_data.get("html_url")
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth Error: {str(e)}")


# 🚀 Main API Route
@app.get("/user/{username}")
def get_user(username: str):
    try:
        repos = get_user_repos(username)

        if repos is None or len(repos) == 0:
            return {
                "success": False,
                "error": "User not found or no public repositories"
            }

        analysis = analyze_repos(repos)

        suggestions = generate_suggestions(
            analysis["total_repos"],
            analysis["total_stars"],
            analysis["languages_used"]
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

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}"
        )