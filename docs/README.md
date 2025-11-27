# FLL Tournament Scheduler - Web Interface

## 🚀 Gebruik (Geen GitHub account nodig!)

### Eenvoudige Methode: Via Web Interface

1. Open de website: `https://koenvanwijk.github.io/ffl-schedule/`
2. Vul de toernooi configuratie in:
   - Aantal teams
   - Aantal tafels
   - Aantal jury rooms
   - Wedstrijden per team
   - Tijdsloten
3. Klik "Genereer Schema"
4. Je wordt doorgeleid naar GitHub om een issue te maken
5. Klik "Submit new issue"
6. **De scheduler start automatisch!** ⚡
7. Wacht 2-5 minuten
8. Schema wordt als artifact toegevoegd aan het issue
9. Download het schema

### Hoe het werkt

1. **Web form** → Genereert een GitHub issue met jouw parameters
2. **GitHub Actions** → Detecteert het issue en start scheduler automatisch
3. **Scheduler draait** → Genereert optimaal schema met constraint programming
4. **Resultaat** → Schema wordt als artifact geüpload + comment in issue

**Geen token, geen login nodig!** Werkt voor iedereen. ✅

## 🔧 Setup (Eenmalig, voor repository owner)

### 1. Activeer GitHub Pages
1. Ga naar je GitHub repository settings
2. Scroll naar "Pages"
3. Selecteer "Deploy from a branch"
4. Kies branch: **main** en folder: **/docs**
5. Klik "Save"

Je website is dan beschikbaar op: `https://koenvanwijk.github.io/ffl-schedule/`

### 2. Zorg dat GitHub Actions enabled is
1. Ga naar Settings → Actions → General
2. Zorg dat "Allow all actions and reusable workflows" is geselecteerd
3. Save

Dat is alles! De website is nu live en werkt automatisch. 🎉

## 📋 Voor Meerdere Gebruikers

Iedereen kan de website gebruiken zonder account:
- ✅ Geen GitHub account nodig
- ✅ Geen token nodig
- ✅ Geen permissions nodig
- ✅ Deel gewoon de website URL!

Issues worden automatisch aangemaakt en verwerkt.

## 🎯 Alternatieve Methode: Handmatig via GitHub

Als je liever direct in GitHub werkt:

1. Ga naar "Issues" tab
2. Klik "New Issue"
3. Add label: `schedule-request`
4. Vul de body in met parameters:
   ```
   ## Toernooi Configuratie
   
   - **Teams:** 40
   - **Tafels:** 6  
   - **Jury Rooms:** 8
   - **Wedstrijden per team:** 4
   - **Tijdsloten:** 40
   ```
5. Submit → Workflow start automatisch!

## Troubleshooting

**"Workflow start niet"**
- Check of de issue het label `schedule-request` heeft
- Controleer of GitHub Actions enabled is

**"Geen oplossing gevonden"**
- Verhoog aantal tijdsloten (van 40 naar 50)
- Verminder aantal teams
- Voeg meer tafels/jury rooms toe

**"Kan artifact niet downloaden"**
- Artifacts vereisen GitHub login
- Login en ga naar Actions → workflow run → Artifacts
