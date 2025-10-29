# Datasets Information 

### 1. Consum Total Agregat (CTA)

Contingut: dades de consum d’aigua agregades per secció censal, districte, codi postal i municipi.

Variables principals: data, ús, consum acumulat (L/dia) i nombre de comptadors.

Observació: les seccions censals corresponen a l’any 2024, i poden variar anualment segons la demografia.

### 2. Repte Consums Anòmals (RCA)

Contingut: factures amb consums modificats o sospitosos d’anomalia.

Informació inclosa: codi de pòlissa, tipus de lectura, codi d’anomalia, codi municipal, període afectat (data inici i final).

Tipus d’anomalies:

- 32768: comptador avariat pendent de substitució.

- 163840: dos períodes consecutius amb lectura igual (consum 0), indicant possible baixada anòmala.

### 3. Fuites d’Aigua – Experiència de Client (FEC)

Contingut: dades sobre fuites d’aigua i la gestió de la incidència amb el client.

Informació inclosa: pòlissa, municipi, dates d’incidència (butlleta, període, requeriment), categoria/assumpte/tema de la incidència.

Altres dades: informació d’usuari (alta i data d’alta) i comunicacions (SMS, correu electrònic, dates, identificadors).

### 4. Incidències en Comptadors Intel·ligents (ICI)

Objectiu: identificar incidències o avaries en comptadors intel·ligents.

Dos conjunts de dades:

Consum diari per pòlissa (POLISSA_SUBM, DATA, CONSUM).

Informació tècnica (POLISSA_SUBM, NUM_COMPLET, DATA_INST_COMP, MARCA_COMP, CODI_MODEL, DIAM_COMP).

Nota: poden existir consums anòmals no vinculats a l’ús real del client.

Information found at:
https://www.abdatachallenge.cat/dades-de-telelectura/ 