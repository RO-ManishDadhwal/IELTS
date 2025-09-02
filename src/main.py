from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict

from curriculum import get_lessons
from sandbox.service import execute_query, reset_db
from ai.tutor import generate_hint, explain_solution
from practice.selector import pick_next
from auth import create_user, authenticate_user, create_access_token

app = FastAPI(title="SQL Tutor")

class QueryRequest(BaseModel):
    query: str

class HintRequest(BaseModel):
    query: str
    schema: str

class ExplainRequest(BaseModel):
    query: str
    expected_output: str

class UserRequest(BaseModel):
    username: str
    password: str

# In-memory practice stats; in production use database
practice_stats: Dict[str, Dict[int, bool]] = {}

@app.get('/lessons')
def lessons():
    return get_lessons()

@app.post('/sandbox/execute')
def sandbox_exec(req: QueryRequest):
    try:
        return execute_query(req.query)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post('/sandbox/reset')
def sandbox_reset():
    reset_db()
    return {'status': 'ok'}

@app.post('/auth/signup')
def signup(user: UserRequest):
    create_user(user.username, user.password)
    return {'status': 'created'}

@app.post('/auth/login')
def login(user: UserRequest):
    if not authenticate_user(user.username, user.password):
        raise HTTPException(status_code=400, detail='Invalid credentials')
    token = create_access_token({'sub': user.username})
    return {'access_token': token}

@app.get('/practice/next')
def practice_next(username: str):
    stats = practice_stats.setdefault(username, {})
    return pick_next(stats)

@app.post('/practice/submit/{exercise_id}')
def practice_submit(exercise_id: int, success: bool, username: str):
    stats = practice_stats.setdefault(username, {})
    stats[exercise_id] = success
    return {'status': 'recorded'}

@app.post('/ai/hint')
def hint(req: HintRequest):
    return {'hint': generate_hint(req.query, req.schema)}

@app.post('/ai/explain')
def explain(req: ExplainRequest):
    return {'explanation': explain_solution(req.query, req.expected_output)}
