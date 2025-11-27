// GitHub repository info
const GITHUB_OWNER = 'koenvanwijk';
const GITHUB_REPO = 'ffl-schedule';

document.getElementById('schedulerForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        num_teams: document.getElementById('numTeams').value,
        num_tables: document.getElementById('numTables').value,
        num_jury_rooms: document.getElementById('numJuryRooms').value,
        matches_per_team: document.getElementById('matchesPerTeam').value,
        num_timeslots: document.getElementById('numTimeslots').value
    };
    
    createIssue(formData);
});

function createIssue(params) {
    // Create issue body with parameters
    const issueTitle = `Schema Request: ${params.num_teams} teams, ${params.num_tables} tafels`;
    const issueBody = `## Toernooi Configuratie

**Automatisch gegenereerd via web interface**

### Parameters
- **Teams:** ${params.num_teams}
- **Tafels:** ${params.num_tables}  
- **Jury Rooms:** ${params.num_jury_rooms}
- **Wedstrijden per team:** ${params.matches_per_team}
- **Tijdsloten:** ${params.num_timeslots}

---
⚙️ *Een GitHub Actions workflow zal automatisch starten om dit schema te genereren.*
📥 *Het resultaat wordt als artifact toegevoegd aan deze issue.*`;

    // URL encode the title and body
    const encodedTitle = encodeURIComponent(issueTitle);
    const encodedBody = encodeURIComponent(issueBody);
    
    // Create GitHub issue URL (without labels - wordt automatisch toegevoegd)
    const issueUrl = `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}/issues/new?title=${encodedTitle}&body=${encodedBody}`;
    
    // Show success message with link
    const statusDiv = document.getElementById('status');
    statusDiv.innerHTML = `
        <strong>✅ Klaar om schema aan te vragen!</strong><br><br>
        <p>Klik op de knop hieronder om een GitHub issue te maken.<br>
        De scheduler start automatisch en het resultaat wordt als artifact toegevoegd.</p>
        <a href="${issueUrl}" target="_blank" class="download-link" style="margin-top: 15px;">
            📝 Maak Issue & Start Scheduler
        </a>
        <br><br>
        <small>💡 Je kunt de status volgen in de GitHub Actions tab</small>
    `;
    statusDiv.className = 'status success';
}
