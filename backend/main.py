from fastapi import FastAPI, HTTPException
from backend.github_service import get_user_repos
from backend.analyzer import analyze_repos, generate_suggestions
from fastapi.middleware.cors import CORSMiddleware
import httpx
from fastapi.responses import RedirectResponse

CLIENT_ID = "Ov23liuu5aXrrJ3iM0dK"
CLIENT_SECRET = "9e26c42eb315033738845e26e4e64550e91fa34d"

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

# Health check (important for deployment platforms)
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Server is running"}

# Login Route
@app.get("/auth/github")
def github_login():
    github_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
    return RedirectResponse(github_url)

# Main API
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
    
# Callback Route

@app.get("/auth/github/callback")
async def github_callback(code: str):

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

    async with httpx.AsyncClient() as client:
        user_res = await client.get(
            "https://api.github.com/user",
            headers={"Authorization": f"token {access_token}"}
        )

    user_data = user_res.json()

    return {
        "username": user_data["login"],
        "avatar": user_data["avatar_url"],
        "profile": user_data["html_url"]
    }