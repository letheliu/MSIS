from fastapi import FastAPI

app = FastAPI(title="MSIS API", version="0.0.1")

@app.get("/")
def root():
    return {"message": "MSIS - Military Document Writing Assistant API"}

@app.get("/health")
def health():
    return {"status": "ok"}
