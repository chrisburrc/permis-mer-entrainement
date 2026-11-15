// Questions d'examen ajoutées au fil des cours.
//
// Ces questions sont partagées avec d'autres élèves : aucune référence personnelle
// (pas de nom, pas de date, pas de lieu ou d'événement privé, pas de « mon bateau »…).
//
// Chaque section apparaît comme un filtre dans l'application. Le glossaire est généré
// à part (glossaire.js) : ne pas l'ajouter ici.
//
// Modèle d'une section :
//   { id: "marees", nom: "Calcul des marées", icone: "🌊", chapitre: "ch 7" }
//
// Modèle d'une question :
//   {
//     id: "marees-001",          // unique et stable : sert à mémoriser ta progression
//     section: "marees",         // id d'une section ci-dessous
//     star: true,                // true = prioritaire pour l'examen
//     q: "Texte de la question (HTML autorisé)",
//     a: "Réponse détaillée, avec chaque étape de calcul (HTML autorisé)",
//     source: "Manuel, ch 7",    // facultatif : chapitre du manuel, jamais de date ni de nom
//   }

const SECTIONS = [];

const QUESTIONS = [];
