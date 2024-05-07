from datetime import datetime

import pyodbc

server = '89.165.36.23'
# database = 'venan_dlv'
sql_user = 'sms'
sql_pass = 'bsh78753'
conn_str = f'DRIVER=ODBC Driver 13 for SQL Server;SERVER={server};UID={sql_user};PWD={sql_pass}'


def get_connection():
    try:
        return pyodbc.connect(conn_str)
    except pyodbc.Error as e:
        return e


def execute_query(query: str, *params):
    con = get_connection()
    if isinstance(con, pyodbc.Error):
        e: pyodbc.Error = con
        return e
    else:
        cursor = con.cursor()
        try:
            cursor = cursor.execute(query, params)
            return cursor
        except pyodbc.Error as e:
            return e


def get_user(phone: str, password: int) -> dict | pyodbc.Error | None:
    cursor = execute_query("SELECT "
                           "[Idnumber] as id,"
                           "[name] as first_name,"
                           "[fam] as last_name,"
                           "[tel] as phone,"
                           "[pass] as password"
                           " FROM [Online_Shop].[dbo].[sms_tel] WHERE [tel] = ? AND [pass] = ?",
                           phone, password)

    if isinstance(cursor, pyodbc.Error):
        return cursor

    row = cursor.fetchone()
    cursor.close()
    if row:
        columns = [column[0] for column in row.cursor_description]
        return dict(zip(columns, row))
    else:
        return row


def get_parcel(code: int) -> dict | pyodbc.Error | None | str:
    cursor = execute_query("SELECT [EtID] as id, [DeliverCode] as 'code', [comment] as 'description', [regdatetime] "
                           " FROM [SmsService].[dbo].[SmsSend] "
                           " WHERE [DeliverCode] = ?",
                           code)

    if isinstance(cursor, pyodbc.Error):
        return cursor

    row = cursor.fetchone()
    cursor.close()
    # row[row.cursor_description.]
    if row:
    #     print(row.cursor_description[2])
        if row[3] is None:
            columns = [column[0] for column in row.cursor_description][:-1]
            return dict(zip(columns, row))
        else:
            return "این کد قبلا استفاده شده است."

    else:
        return row


def set_parcel_delivered(p_id: int, user_id: int) -> pyodbc.Error | None:
    cursor = execute_query("UPDATE [SmsService].[dbo].[SmsSend] SET [regdatetime]=?,[app_id]=? WHERE [EtID]=?",
                           datetime.now(), user_id, p_id)

    if isinstance(cursor, pyodbc.Error):
        return cursor

    cursor.commit()
    cursor.close()
    return None

