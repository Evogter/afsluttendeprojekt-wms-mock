# Eksamensprojekt – WMS API Mock

##  Projektbeskrivelse

Dette projekt er udviklet som en del af mit afsluttende eksamensprojekt på Københavns Erhvervsakademi. Formålet er at simulere API-kald til Dell Wyse Management Suite (WMS) og undersøge, hvordan man kan hente og visualisere overvågningsdata fra Thin Clients – uden adgang til et rigtigt WMS-system.

## Teknisk opsætning

Projektet består af følgende komponenter:

- **Postman Mock Server**  
  Bruges til at simulere WMS REST API-endpoints med realistiske eksempler.
- **Python API-klient** (`api/wms_client.py`)  
  Sender requests til mock-serveren og henter fx status og firmware-data for enheder.
- **Flask Dashboard** (`dashboard/app.py`)  
  En webapplikation som viser enhedsstatus og opdateringsniveau i browseren.
- **Virtuelt miljø (`venv/`)**  
  Indeholder alle nødvendige Python-pakker (requests, flask, tabulate m.fl.)
- **Dokumentation**  
  Indeholder systemoversigt og projektbeskrivelse.


