from fastapi import FastAPI

app = FastAPI(
    title="SolveSphere API",
    description="SolveSphere connects societal challenges in Jharkhand with Higher Education Institutions, industry and other innovation partners",
    version="1.0.0",
)


@app.get("/health")
def get_health():
    return {
        "status": "healthy",
        "service": "SolveSphere API",
    }
