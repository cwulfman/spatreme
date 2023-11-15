SPARQL_ENDPOINT=http://147.182.188.37:7200/repositories/spatrem python -m uvicorn wsgi:app --workers 2 --host 127.0.0.1 --reload
