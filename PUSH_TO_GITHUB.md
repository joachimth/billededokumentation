# 🚀 Sådan pusher du de optimerede ændringer til GitHub

## Trin 1: Naviger til dit lokale repository
```bash
cd /sti/til/dit/lokale/billededokumentation
```

## Trin 2: Tjek at dine ændringer er commit'et
```bash
git status
```

Du skulle gerne se noget lignende:
```
On branch master
Your branch is ahead of 'origin/master' by 3 commits.
  (use "git push" to publish your local commits)
```

## Trin 3: Push til GitHub
```bash
git push origin master
```

## Hvis du får authentication fejl:
### Med password/token (anbefalet):
```bash
git push https://github.com/joachimth/billededokumentation.git master
```
Så bliver du bedt om username og Personal Access Token

### Med SSH (hvis opsat):
```bash
git push git@github.com:joachimth/billededokumentation.git master
```

## Trin 4: Verificer på GitHub
Gå til: https://github.com/joachimth/billededokumentation

Du skulle nu se alle de optimerede filer og commits.

## 📋 Hvad der bliver push'et:
- ✅ **app_web.py** - Komplet optimeret web version
- ✅ **app.py** - Forbedret kommandolinje version  
- ✅ **static/** - Ny web filer (CSS/JS)
- ✅ **templates/** - Ny HTML template
- ✅ **INSTALLATION.md** - Komplet installationsguide
- ✅ **requirements.txt** - Opdaterede dependencies
- ✅ **README.md** - Forbedret dokumentation
- ✅ **Alle commits** med detaljerede beskrivelser

## 🔄 Har du allerede pushes?
Hvis du allerede har lavet commits siden sidst, kan du pull'e mine ændringer:
```bash
git pull origin master
```

## 📖 Hvis du mangler min branch:
Hvis du ikke kan se mine commits, kan det være at du arbejder på en anden branch. Mine commits er på `master` branch'en.

---
**Kort sagt:** Kør `git push origin master` i dit lokale repository for at uploade alle optimeringer! 🚀