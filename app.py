from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import io
import base64
import time

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def calculate_D_AB(...):  # Votre fonction existante
    # Contenu inchangé
    return np.exp(D)

def objective(...):  # Votre fonction existante
    # Contenu inchangé
    return np.sum((D_AB_calculated - D_AB_exp)**2)

@app.get("/", response_class=HTMLResponse)
def input_data(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/calculate")
def calculate(D_AB_exp: float = Form(...), T: float = Form(...), Xa: float = Form(...),
              λ_a: str = Form(...), λ_b: str = Form(...), q_a: float = Form(...),
              q_b: float = Form(...), D_AB0: float = Form(...), D_BA0: float = Form(...)):
    λ_a = eval(λ_a)
    λ_b = eval(λ_b)

    # Logique similaire à celle de votre Flask app
    # ...

    # Pour retourner des images, convertissez-les en format adapté ou servez-les via un endpoint statique
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    graph = base64.b64encode(buffer.getvalue()).decode()
    plt.close()

    return templates.TemplateResponse("result.html", {"request": Request,
                                                      "a_AB_opt": a_AB_opt,
                                                      "a_BA_opt": a_BA_opt,
                                                      "D_AB_opt": D_AB_opt,
                                                      "error": error,
                                                      "iteration": iteration,
                                                      "execution_time": execution_time,
                                                      "graph": graph})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
