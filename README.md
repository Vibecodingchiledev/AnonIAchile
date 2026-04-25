# Privacy Gateway CL MVP

Backend FastAPI + dashboard HTML para vender el MVP de anonimización y trazabilidad.

## Qué incluye
- Dashboard web en `/`
- API FastAPI
- Login demo
- Anonimización de texto y archivos UTF-8
- Reglas de detección para Chile: RUT, teléfono, patente, email, fecha y direcciones simples
- Reemplazos inteligentes con `anonymize_improved.py`
- Reportes JSON por job en `reports/`

## Ejecutar
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Luego abre:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

## Usuarios demo
- admin@demo.cl / demo123
- auditor@demo.cl / demo123
- researcher@demo.cl / demo123

## Endpoints
- `GET /api/health`
- `POST /api/login`
- `POST /api/anonymize`
- `POST /api/anonymize-file`
- `GET /api/jobs`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/report`

## Avisos
- Este MVP usa detección heurística, no el pipeline NER completo.
- La custodia HSM/PQC está marcada como simulada.
- No usar en producción sin reforzar autenticación, storage, colas, cifrado y evaluación de reidentificación.
