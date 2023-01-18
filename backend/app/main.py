import uvicorn

from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

from typing import List
import fastapi as _fastapi
import fastapi.security as _security

import sqlalchemy.orm as _orm

import app.services as _services
import app.schemas as _schemas

from fastapi.middleware.cors import CORSMiddleware

from pathlib import Path

from app.config import Configs


def init_app():
    app = _fastapi.FastAPI(
        title="OAuth2 App",
        description="OAuth2 API Page",
        version="1"
    )

    app.mount("/static", StaticFiles(directory="static"), name="static")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=Configs.origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    
    @app.get("/api")
    async def root():
        port = str(Configs.REMOTE_PORT)
        protocole = Configs.REMOTE_PROTOCOLE
        host = Configs.REMOTE_HOST
        return {"message": "Welcome to OAuth2 app!", "host": host, "port":port, "protocole":protocole}    

    @app.get("/test")
    async def test():
        return {"message": "Awesome welcome"}

    @app.post("/api/token")
    async def generate_token(form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
                             db: _orm.Session = _fastapi.Depends(_services.get_db), ):
        user = await _services.authenticate_user(form_data.username, form_data.password, db)

        if not user:
            raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")

        return await _services.create_token(user, db)

    @app.post("/token")
    async def verify_token(token: str = None, db: _orm.Session = _fastapi.Depends(_services.get_db), ):
        if token is None:
            raise _fastapi.HTTPException(status_code=500, detail="Error")
        return await _services.parse_user(token, db)
    
    @app.get("/token")
    async def get_user(token: str = None, db: _orm.Session = _fastapi.Depends(_services.get_db), ):
        return verify_token(token, db)

    @app.get("/api/users/me", response_model=_schemas.User)
    async def get_user(user: _schemas.User = _fastapi.Depends(_services.get_current_user)):
        return user

    @app.post("/api/leads", response_model=_schemas.Lead)
    async def create_lead(lead: _schemas.LeadCreate, user: _schemas.User = _fastapi.Depends(_services.get_current_user),
                          db: _orm.Session = _fastapi.Depends(_services.get_db), ):
        return await _services.create_lead(user=user, db=db, lead=lead)

    @app.get("/api/leads", response_model=List[_schemas.Lead])
    async def get_leads(user: _schemas.User = _fastapi.Depends(_services.get_current_user),
                        db: _orm.Session = _fastapi.Depends(_services.get_db), ):
        return await _services.get_leads(user=user, db=db)

    @app.get("/api/leads/{lead_id}", status_code=200)
    async def get_lead(lead_id: int, user: _schemas.User = _fastapi.Depends(_services.get_current_user),
                       db: _orm.Session = _fastapi.Depends(_services.get_db), ):
        return await _services.get_lead(lead_id, user, db)

    @app.delete("/api/leads/{lead_id}", status_code=204)
    async def delete_lead(lead_id: int, user: _schemas.User = _fastapi.Depends(_services.get_current_user),
                          db: _orm.Session = _fastapi.Depends(_services.get_db), ):
        await _services.delete_lead(lead_id, user, db)
        return {"message", "Successfully Deleted"}

    @app.put("/api/leads/{lead_id}", status_code=200)
    async def update_lead(lead_id: int, lead: _schemas.LeadCreate,
                          user: _schemas.User = _fastapi.Depends(_services.get_current_user),
                          db: _orm.Session = _fastapi.Depends(_services.get_db), ):
        await _services.update_lead(lead_id, lead, user, db)
        return {"message", "Successfully Updated"}

    @app.on_event("startup")
    async def startup():
        BASE_DIR = Path(__file__).resolve().parent.parent
        # Specify path
        path = str(BASE_DIR) + '\\test.db'        
        isExist = os.path.exists(path)
        if not isExist:
            _services.create_database()

    @app.on_event("shutdown")
    async def shutdown():
        _services.close_db()

    @app.get("/")
    async def docs_redirect():
        return RedirectResponse(url='/docs')

    @app.get('/favicon.ico')
    async def favicon():
        file_name = "favicon.ico"
        file_path = os.path.join(app.root_path, "static")
        return FileResponse(path=file_path, headers={"Content-Disposition": "attachment; filename=" + file_name})

    @app.post("/api/users")
    async def create_user(user: _schemas.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)):
        db_user = await _services.get_user_by_email(user.email, db)
        if db_user:
            raise _fastapi.HTTPException(status_code=400, detail="Email already in use")
        user = await _services.create_user(user, db)
        return await _services.create_token(user, db)

    return app


app = init_app()

if __name__ =="__main__":
    app = init_app()
    uvicorn.run(app, host=Configs.HOST, port=Configs.PORT, reload=True)

def start():
    """Launched with 'poetry run start' at root level """
    uvicorn.run("app.main:app", host=Configs.HOST, port=Configs.PORT, reload=True)
