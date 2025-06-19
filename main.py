from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from bs4 import BeautifulSoup
import os
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/outline")
async def get_country_outline(country: str = Query(..., min_length=1)):
    url = f"https://en.wikipedia.org/wiki/{country.replace(' ', '_')}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10)
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail="Page not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    soup = BeautifulSoup(response.text, "html.parser")
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    markdown = "## Contents\n\n"
    markdown += f"# {country.title()}\n\n"

    for tag in headings:
        level = int(tag.name[1])
        text = tag.get_text().strip()
        if text.lower() == "contents":
            continue
        markdown += f"{'#' * level} {text}\n\n"

    return {"markdown_outline": markdown}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
