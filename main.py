import pyodbc
from fastapi import FastAPI, Request, Response
import database as db
import re

app = FastAPI()

version = 1


def response(resp: Response, data=None, overwrite_code: int | None = None):
    if isinstance(data, pyodbc.Error):
        status = 0
        error = data.args[0]
        msg = f"Error in database {data.args[0]}"
        data = {}
        code = 505
    elif isinstance(data, str):
        status = 0
        error = None
        msg = data
        data = None
        code = 400
    else:
        status = 1
        error = None
        msg = None
        code = 200

    if overwrite_code:
        code = overwrite_code

    resp.status_code = code
    return json(status, error, msg, data)


def json(status: int, error: dict | None, msg: str | None, data: dict | None):
    res = {"status": status, "error": error, "message": msg, "data": {} if data is None and status == 1 else data}
    return {key: value for key, value in res.items() if value is not None}


@app.get("/")
async def root(res: Response):
    con = db.get_connection()

    if isinstance(con, pyodbc.Error):
        res.status_code = 500
        return f"Sql Error: {con.args[0]}"
    else:
        con.close()
        return "Hello World"


@app.get(f"/v{version}/check")
async def check_connection(res: Response):
    con = db.get_connection()
    if isinstance(con, pyodbc.Error):
        return response(res, con)
    else:
        return response(res)


@app.post(f"/v{version}/login")
async def login(req: Request, res: Response):
    body = await req.json()
    if "phone" in body:
        phone = body["phone"]
    else:
        return response(res, "Phone Required")

    if "password" in body:
        password = body["password"]
    else:
        return response(res, "Password Required")

    if not _verify_phone(phone):
        return response(res, "Invalid Phone")

    if not isinstance(password, int):
        return response(res, "Invalid Password")

    user = db.get_user(phone, password)
    if user:
        return response(res, user)
    else:
        return response(res, "Invalid Phone Or Password", 404)


@app.get(f"/v{version}/parcel")
async def check_parcel_code(code, res: Response):
    if code is None:
        return response(res, "Code Required")

    if not code.isdigit():
        return response(res, "Code is number")

    parcel = db.get_parcel(int(code))

    if parcel:
        return response(res, parcel)
    else:
        return response(res, "Not Found", 404)


@app.post(f"/v{version}/parcel")
async def deliver_parcel(req: Request, res: Response):
    body = await req.json()
    if "id" in body:
        p_id = body["id"]
    else:
        return response(res, "Id Required")

    if "user_id" in body:
        u_id = body["user_id"]
    else:
        return response(res, "User Required")

    result = db.set_parcel_delivered(p_id, u_id)
    return response(res, result)


async def _verify_phone(phone):
    pattern = r'^09\d{9}$'
    return re.match(pattern, phone)
