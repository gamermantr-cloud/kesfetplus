from fastapi import FastAPI

app = FastAPI(title="KesfetPlus")


@app.get("/")
def read_root():
    return {"name": "KesfetPlus", "status": "running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}
