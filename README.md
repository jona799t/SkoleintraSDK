# SkoleIntra API
Log ind på ItsLearnings skoleintra kun ved brug af Python

# Installation
```
pip install skoleintra
```

# Brug
En fuld dokumentation er ikke udgivet endnu men her er basis, der er også kun ugeplanen som man kan finde lige nu.
```python
from skoleintra import Skoleintra

baseUrl = "https://minskole.m.skoleintra.dk"

skoleintraClient = Skoleintra(brugernavn="brugernavn", adgangskode="adganskode", url=baseUrl)
ugeplan = skoleintraClient.getWeeklyplans(week=10, year=2022)

print(ugeplan) #Output: Ugeplanen for den uge
```

# To Do
   - Flere funktioner

# Dokumentation
Kommer snart!
