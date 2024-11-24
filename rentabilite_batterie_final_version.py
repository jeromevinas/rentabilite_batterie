from flask import Flask, render_template_string, request
import pandas as pd

app = Flask(__name__)

# Données des tarifs d'électricité pour la France et la Belgique
electricity_data = {
    'Pays': ['France', 'France', 'Belgique', 'Belgique', 'Belgique'],
    'Logo': [
        'https://upload.wikimedia.org/wikipedia/commons/8/8f/Logo-engie.svg',  # Engie
        'https://upload.wikimedia.org/wikipedia/fr/f/f7/Logo_TotalEnergies.svg',  # TotalEnergies
        'https://upload.wikimedia.org/wikipedia/commons/8/8f/Logo-engie.svg',  # Engie Belgique
        'https://upload.wikimedia.org/wikipedia/fr/c/c6/Logo_Luminus.svg',  # Luminus
        'https://upload.wikimedia.org/wikipedia/commons/b/b0/Eneco_logo.png'  # Eneco
    ],
    'Prix électricité (€/kWh)': [0.22, 0.20, 0.27, 0.25, 0.26],
    'Tarif de rachat (€/kWh)': [0.09, 0.08, 0.10, 0.10, 0.10]
}
electricity_df = pd.DataFrame(electricity_data)

# Données des fournisseurs de batteries
battery_data = {
    'Logo': [
        'https://upload.wikimedia.org/wikipedia/commons/b/bb/Tesla_T_symbol.svg',  # Tesla
        'https://upload.wikimedia.org/wikipedia/commons/3/33/LG_Chem_logo_%28english%29.svg',  # LG Chem
        'https://upload.wikimedia.org/wikipedia/en/0/04/Huawei_Standard_logo.svg',  # Huawei
        'https://upload.wikimedia.org/wikipedia/commons/9/95/Panasonic_logo.svg',  # Panasonic
        'https://upload.wikimedia.org/wikipedia/commons/9/93/Sonnen_logo.png'  # Sonnen
    ],
    'Modèle de Batterie': ['Powerwall 2', 'RESU 6', 'LUNA 2000', 'EverVolt Standard', 'SonnenBatterie 10'],
    'Capacité (kWh)': [13.5, 6.5, 10, 11.4, 22],
    'Prix estimé (€)': [8730, 3700, 6200, 14000, 9400],
    'Durée de vie estimée (années)': [10, 10, 10, 10, 10],
}
battery_df = pd.DataFrame(battery_data)

@app.route("/", methods=["GET", "POST"])
def home():
    results = None
    form_data = {
        "cost": request.form.get("cost", ""),
        "capacity": request.form.get("capacity", ""),
        "lifetime": request.form.get("lifetime", ""),
        "excess": request.form.get("excess", ""),
        "grid_price": request.form.get("grid_price", ""),
        "buyback_price": request.form.get("buyback_price", ""),
        "discount_rate": request.form.get("discount_rate", "")
    }

    if request.method == "POST":
        try:
            cost = float(form_data["cost"])
            capacity = float(form_data["capacity"])
            lifetime = int(form_data["lifetime"])
            excess = float(form_data["excess"])
            grid_price = float(form_data["grid_price"])
            buyback_price = float(form_data["buyback_price"])
            discount_rate = float(form_data["discount_rate"]) / 100

            # Calculs financiers
            savings = excess * (grid_price - buyback_price)
            amortization = cost / lifetime
            net_profit = savings - amortization
            cumulative_npv = 0

            for t in range(1, lifetime + 1):
                yearly_npv = (savings - amortization) / ((1 + discount_rate) ** t)
                cumulative_npv += yearly_npv

            results = {
                "savings": round(savings, 2),
                "amortization": round(amortization, 2),
                "net_profit": round(net_profit, 2),
                "npv": round(cumulative_npv, 2),
            }
        except Exception as e:
            results = {"error": str(e)}

    html_template = """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Rentabilité Batterie</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
        <style>
            body {
                background-color: #f8f9fa;
            }
            .container {
                margin-top: 20px;
                max-width: 1200px;
            }
            .card {
                margin-top: 20px;
            }
            .tooltip-icon {
                font-size: 1.2rem;
                color: #6c757d;
                cursor: pointer;
                margin-left: 5px;
            }
            img.logo {
                max-height: 50px;
                max-width: 100px;
                object-fit: contain;
            }
            .hidden {
                display: none;
            }
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function () {
                const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
                tooltipTriggerList.map(function (tooltipTriggerEl) {
                    return new bootstrap.Tooltip(tooltipTriggerEl)
                });
            });

            function toggleVisibility(sectionId, show) {
                const section = document.getElementById(sectionId);
                if (show) {
                    section.classList.remove("hidden");
                } else {
                    section.classList.add("hidden");
                }
            }

            function showBatteryTable(gridPrice, buybackPrice) {
                document.getElementById("grid_price").value = gridPrice;
                document.getElementById("buyback_price").value = buybackPrice;
                toggleVisibility("battery-table", true);
                toggleVisibility("tariff-table", false);
            }

            function showForm(cost, capacity, lifetime) {
                document.getElementById("cost").value = cost;
                document.getElementById("capacity").value = capacity;
                document.getElementById("lifetime").value = lifetime;
                toggleVisibility("form-section", true);
                toggleVisibility("battery-table", false);
            }

            function restartSimulation() {
                toggleVisibility("tariff-table", true);
                toggleVisibility("battery-table", false);
                toggleVisibility("form-section", false);
                toggleVisibility("results-section", false);
                document.getElementById("form-section").reset();
            }
        </script>
    </head>
    <body>
        <div class="container">
            <h1 class="text-center">Calcul de la Rentabilité des Batteries</h1>
            <!-- Tableau des tarifs -->
            <div id="tariff-table" class="table-wrapper {% if results %}hidden{% endif %}">
                <h3>Tarifs d'électricité</h3>
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Pays</th>
                            <th>Opérateur</th>
                            <th>Prix électricité</th>
                            <th>Tarif de rachat</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for index, row in electricity_df.iterrows() %}
                        <tr>
                            <td>{{ row['Pays'] }}</td>
                            <td><img src="{{ row['Logo'] }}" class="logo"></td>
                            <td>{{ row['Prix électricité (€/kWh)'] }}</td>
                            <td>{{ row['Tarif de rachat (€/kWh)'] }}</td>
                            <td><button class="btn btn-secondary btn-sm" onclick="showBatteryTable({{ row['Prix électricité (€/kWh)'] }}, {{ row['Tarif de rachat (€/kWh)'] }})">Choisir</button></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            <!-- Tableau des fournisseurs de batteries -->
            <div id="battery-table" class="table-wrapper hidden">
                <h3>Fournisseurs de batteries</h3>
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Fournisseur</th>
                            <th>Modèle</th>
                            <th>Capacité (kWh)</th>
                            <th>Prix (€)</th>
                            <th>Durée de vie (ans)</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for index, row in battery_df.iterrows() %}
                        <tr>
                            <td><img src="{{ row['Logo'] }}" class="logo"></td>
                            <td>{{ row['Modèle de Batterie'] }}</td>
                            <td>{{ row['Capacité (kWh)'] }}</td>
                            <td>{{ row['Prix estimé (€)'] }}</td>
                            <td>{{ row['Durée de vie estimée (années)'] }}</td>
                            <td><button class="btn btn-secondary btn-sm" onclick="showForm({{ row['Prix estimé (€)'] }}, {{ row['Capacité (kWh)'] }}, {{ row['Durée de vie estimée (années)'] }})">Choisir</button></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            <!-- Formulaire -->
            <div id="form-section" class="hidden">
                <form method="POST" class="card p-4 shadow-sm">
                    <h2 class="text-secondary">Données à renseigner</h2>
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="cost" class="form-label">
                                Coût d'achat (€)
                                <span class="tooltip-icon" data-bs-toggle="tooltip" data-bs-placement="top" title="Coût initial d'achat de la batterie.">?</span>
                            </label>
                            <input type="number" id="cost" name="cost" class="form-control" step="0.01" value="{{ form_data['cost'] }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="capacity" class="form-label">
                                Capacité (kWh)
                                <span class="tooltip-icon" data-bs-toggle="tooltip" data-bs-placement="top" title="Capacité de stockage énergétique de la batterie.">?</span>
                            </label>
                            <input type="number" id="capacity" name="capacity" class="form-control" step="0.01" value="{{ form_data['capacity'] }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="lifetime" class="form-label">
                                Durée de vie (ans)
                                <span class="tooltip-icon" data-bs-toggle="tooltip" data-bs-placement="top" title="Durée estimée pendant laquelle la batterie reste opérationnelle.">?</span>
                            </label>
                            <input type="number" id="lifetime" name="lifetime" class="form-control" value="{{ form_data['lifetime'] }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="excess" class="form-label">
                                Production excédentaire (kWh)
                                <span class="tooltip-icon" data-bs-toggle="tooltip" data-bs-placement="top" title="Quantité d'énergie produite en excès par vos panneaux solaires.">?</span>
                            </label>
                            <input type="number" id="excess" name="excess" class="form-control" step="0.01" value="{{ form_data['excess'] }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="grid_price" class="form-label">
                                Prix électricité (€/kWh)
                                <span class="tooltip-icon" data-bs-toggle="tooltip" data-bs-placement="top" title="Prix moyen de l'électricité que vous achetez au fournisseur.">?</span>
                            </label>
                            <input type="number" id="grid_price" name="grid_price" class="form-control" step="0.01" value="{{ form_data['grid_price'] }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="buyback_price" class="form-label">
                                Tarif de rachat (€/kWh)
                                <span class="tooltip-icon" data-bs-toggle="tooltip" data-bs-placement="top" title="Tarif auquel le fournisseur rachète votre électricité excédentaire.">?</span>
                            </label>
                            <input type="number" id="buyback_price" name="buyback_price" class="form-control" step="0.01" value="{{ form_data['buyback_price'] }}" required>
                        </div>
                        <div class="col-md-6 mb-3">
                            <label for="discount_rate" class="form-label">
                                Taux d'actualisation (%)
                                <span class="tooltip-icon" data-bs-toggle="tooltip" data-bs-placement="top" title="Taux utilisé pour actualiser les valeurs futures.">?</span>
                            </label>
                            <input type="number" id="discount_rate" name="discount_rate" class="form-control" step="0.01" value="{{ form_data['discount_rate'] }}" required>
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Calculer</button>
                </form>
            </div>
            {% if results %}
            <div id="results-section" class="card p-4 shadow-sm mt-3">
                <h2 class="text-success">Résultats</h2>
                {% if 'error' in results %}
                <p class="text-danger">{{ results['error'] }}</p>
                {% else %}
                <ul class="list-group">
                    <li class="list-group-item">Économies annuelles : {{ results['savings'] }} €</li>
                    <li class="list-group-item">Amortissement annuel : {{ results['amortization'] }} €</li>
                    <li class="list-group-item">Rentabilité annuelle nette : {{ results['net_profit'] }} €</li>
                    <li class="list-group-item">Valeur Actualisée Nette : {{ results['npv'] }} €</li>
                </ul>
                <button class="btn btn-secondary mt-3" onclick="restartSimulation()">Refaire une simulation</button>
                {% endif %}
            </div>
            {% endif %}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    return render_template_string(html_template, results=results, form_data=form_data, electricity_df=electricity_df, battery_df=battery_df)

if __name__ == "__main__":
    app.run(debug=True, port=8080)