# cocktail catalogue
## Live demo:
- Frontend https://drinkly.onrender.com/
- Backend https://cocktail-catalogue.onrender.com/api/

## Installation on a local machine
```bash
git clone https://github.com/Konstantin-Svt/cocktail-catalogue.git
cd cocktail-catalogue
```
### Backend
- Install and run Docker
- In the working directory ```cocktail-catalogue``` run in terminal:
```bash
docker compose build
docker compose up
```

- API is available at http://127.0.0.1:8000/api/
- Documentation at http://127.0.0.1:8000/api/docs/swagger/ as UI or http://127.0.0.1:8000/api/docs/ as YAML file

### Frontend
- Install Node.js & npm
- Set env varialble "VITE_API_URL"
- on Windows:
```bash
set VITE_API_URL=http://127.0.0.1:8000/api
```
- on MacOS:
```bash
export VITE_API_URL="http://127.0.0.1:8000/api"
```
- after that:
```bash
cd frontend
npm install --force
npm start
```

- Site is available at http://localhost:5173/