# ManageExpenses

Minimalistic telegram bot for managing expenses. Made with love 💘

## Deploying

1. Set up and activate your virtual environment. For example:

```bash
python -m venv .venv &&
.venv\Scripts\activate
```

2. Set `DB_URL` and `BOT_TOKEN` environmental variables in format (for supported databases
   visit [tortoise docs](https://tortoise.github.io/databases.html)):

```
DB_URL=asyncpg://postgres:postgres@localhost:5432/manage_expenses
BOT_TOKEN=SUPER_SECRET_TOKEN
```

3. Install requirements

```
pip install -r requirements.txt
```

## License

[MIT](https://choosealicense.com/licenses/mit/)