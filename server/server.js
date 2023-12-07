const express = require('express');
const { spawn } = require('child_process');
const bodyParser = require('body-parser');
const app = express();
const port = 3000;

// Middleware pour parser le JSON
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serveur la page HTML avec le formulaire
app.get('/', (req, res) => {
    res.send(`
        <form action="/submit-json" method="post">
            <textarea name="jsonData" rows="10" cols="50"></textarea><br>
            <input type="submit" value="Envoyer">
        </form>
    `);
});

// Gestionnaire de formulaire
app.post('/submit-json', (req, res) => {
    const jsonData = req.body.jsonData;
    executePythonScript(jsonData, res);
});

function executePythonScript(data, res) {
    const pythonProcess = spawn('python', ['./video_generator.py', data]);

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Sortie Python: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Erreur Python: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Processus Python terminé avec le code ${code}`);
        res.send('Vidéo générée avec succès !');
    });
}

app.listen(port, () => {
    console.log(`Serveur démarré sur http://localhost:${port}`);
});
