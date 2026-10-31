# Blood and Organ Donor Finder
Group project (Python, Django, SQLite, Bootstrap).

## Useful addresses (local)

| Page | Address |
|---|---|
| Home | http://127.0.0.1:8000/ |
| Register | /accounts/register/ |
| Find donors | /donors/search/ |
| My donor profile | /donors/profile/ |
| Organ pledge | /organs/pledge-info/ |
| Privacy policy | /trust/privacy/ |
| Admin | /admin/ |

## Environment variables (`.env`)

```
SECRET_KEY=a-long-random-text
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=
```
Never commit `.env`. Set `DEBUG=False` only on the server.