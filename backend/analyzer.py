def analyze_repos(repos):
    total_repos = len(repos)
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    languages = {}

    for repo in repos:
        lang = repo.get("language")
        if lang:
            languages[lang] = languages.get(lang, 0) + 1

    top_language = max(languages, key=languages.get) if languages else None
    score = calculate_dev_score(total_repos, total_stars, languages)

    return {
        "total_repos": total_repos,
        "total_stars": total_stars,
        "top_language": top_language,
        "languages_used": languages,
        "dev_score": score
    }

def calculate_dev_score(total_repos, total_stars, languages):
    score = 0
    score += min(total_repos * 2, 40)
    score += min(total_stars // 100, 40)
    score += min(len(languages) * 5, 20)
    return score

def generate_suggestions(total_repos, total_stars, languages):
    suggestions = []

    if total_repos < 5:
        suggestions.append("Build more public projects to showcase consistency.")
    if total_stars < 10:
        suggestions.append("Focus on creating projects that solve real problems to gain visibility.")
    if len(languages) < 2:
        suggestions.append("Try exploring more technologies to diversify your profile.")
    if total_repos > 10 and total_stars > 50:
        suggestions.append("Great profile! Now focus on building scalable or production-level systems.")
    if not suggestions:
        suggestions.append("Strong profile! Keep pushing towards impactful and unique projects.")

    return suggestions