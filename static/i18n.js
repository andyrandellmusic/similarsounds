/* SimilarSounds translations.
 *
 * The page is written in English. This file swaps visible text, placeholders, tooltips and
 * screen-reader labels into the chosen language, and keeps doing so as new content appears
 * (results, pop-ups, the set panel). Track titles, artists, labels and sub-genre names are
 * never translated. The choice is remembered on the device (localStorage "ss_lang").
 *
 * Columns in T and P: es, fr, de, it, pt, nl.
 */
(function () {
  const LANGS = [
    ["en", "English"], ["es", "Español"], ["fr", "Français"], ["de", "Deutsch"],
    ["it", "Italiano"], ["pt", "Português"], ["nl", "Nederlands"],
  ];
  const COL = { es: 0, fr: 1, de: 2, it: 3, pt: 4, nl: 5 };

  // ---------- exact phrases
  const T = {
    "Find": ["Buscar", "Rechercher", "Suchen", "Cerca", "Buscar", "Zoeken"],
    "Filters": ["Filtros", "Filtres", "Filter", "Filtri", "Filtros", "Filters"],
    "Released": ["Lanzado", "Sortie", "Veröffentlicht", "Uscita", "Lançamento", "Uitgebracht"],
    "30 days": ["30 días", "30 jours", "30 Tage", "30 giorni", "30 dias", "30 dagen"],
    "3 months": ["3 meses", "3 mois", "3 Monate", "3 mesi", "3 meses", "3 maanden"],
    "1 year": ["1 año", "1 an", "1 Jahr", "1 anno", "1 ano", "1 jaar"],
    "All time": ["Siempre", "Tout", "Alle", "Sempre", "Sempre", "Altijd"],
    "Sub-genre": ["Subgénero", "Sous-genre", "Subgenre", "Sottogenere", "Subgênero", "Subgenre"],
    "Any": ["Cualquiera", "Tous", "Alle", "Qualsiasi", "Qualquer", "Alle"],
    "any sub-genre": ["cualquier subgénero", "tous sous-genres", "jedes Subgenre", "qualsiasi sottogenere", "qualquer subgênero", "elk subgenre"],
    "harmonic": ["armónico", "harmonique", "harmonisch", "armonico", "harmônico", "harmonisch"],
    "BPM range": ["Rango de BPM", "Plage de BPM", "BPM-Bereich", "Intervallo BPM", "Faixa de BPM", "BPM-bereik"],
    "Harmonic matches only": ["Solo coincidencias armónicas", "Uniquement en harmonie", "Nur harmonische Treffer", "Solo abbinamenti armonici", "Só combinações harmônicas", "Alleen harmonische matches"],
    "Try a fresh release": ["Prueba un lanzamiento nuevo", "Essayez une nouveauté", "Probier einen neuen Release", "Prova una nuova uscita", "Experimente um lançamento novo", "Probeer een nieuwe release"],
    "Or try a fresh release": ["O prueba un lanzamiento nuevo", "Ou essayez une nouveauté", "Oder probier einen neuen Release", "Oppure prova una nuova uscita", "Ou experimente um lançamento novo", "Of probeer een nieuwe release"],
    "Pick a track": ["Elige un tema", "Choisissez un titre", "Track wählen", "Scegli un brano", "Escolha uma faixa", "Kies een track"],
    "Type an artist or paste a YouTube, SoundCloud or Beatport link.": ["Escribe un artista o pega un enlace de YouTube, SoundCloud o Beatport.", "Tapez un artiste ou collez un lien YouTube, SoundCloud ou Beatport.", "Gib einen Artist ein oder füge einen YouTube-, SoundCloud- oder Beatport-Link ein.", "Scrivi un artista o incolla un link di YouTube, SoundCloud o Beatport.", "Digite um artista ou cole um link do YouTube, SoundCloud ou Beatport.", "Typ een artiest of plak een YouTube-, SoundCloud- of Beatport-link."],
    "Get matches": ["Obtén coincidencias", "Obtenez des correspondances", "Treffer erhalten", "Ottieni abbinamenti", "Receba sugestões", "Krijg matches"],
    "The latest house music that fits its key, BPM, energy and sound.": ["Lo último en música house que encaja con su tonalidad, BPM, energía y sonido.", "La toute dernière house music qui colle à sa tonalité, son BPM, son énergie et son son.", "Die neueste House-Musik, die zu Tonart, BPM, Energie und Sound passt.", "L'ultima musica house in linea con tonalità, BPM, energia e suono.", "O mais novo em house music que combina com o tom, BPM, energia e som.", "De nieuwste housemuziek die past bij toonsoort, BPM, energie en sound."],
    "Build your set": ["Arma tu set", "Construisez votre set", "Stell dein Set zusammen", "Crea il tuo set", "Monte seu set", "Bouw je set"],
    "Line tracks up and see which ones mix smoothly.": ["Ordena los temas y mira cuáles mezclan bien.", "Alignez les titres et voyez lesquels s'enchaînent bien.", "Ordne Tracks an und sieh, welche gut ineinander übergehen.", "Metti in fila i brani e scopri quali si mixano bene.", "Organize as faixas e veja quais mixam bem.", "Zet tracks op volgorde en zie welke soepel mixen."],
    "Paste a track.": ["Pega un tema.", "Collez un titre.", "Füge einen Track ein.", "Incolla un brano.", "Cole uma faixa.", "Plak een track."],
    "the latest": ["lo último", "la toute dernière", "die neueste", "l'ultima", "o mais novo", "de nieuwste"],
    "Start typing an artist… or paste a YouTube, SoundCloud, Beatport link": ["Escribe un artista… o pega un enlace de YouTube, SoundCloud o Beatport", "Tapez un artiste… ou collez un lien YouTube, SoundCloud, Beatport", "Artist eingeben… oder YouTube-, SoundCloud-, Beatport-Link einfügen", "Scrivi un artista… o incolla un link YouTube, SoundCloud, Beatport", "Digite um artista… ou cole um link do YouTube, SoundCloud, Beatport", "Typ een artiest… of plak een YouTube-, SoundCloud-, Beatport-link"],
    "Clear search and start again": ["Borrar la búsqueda y empezar de nuevo", "Effacer la recherche et recommencer", "Suche löschen und neu starten", "Cancella la ricerca e ricomincia", "Limpar a busca e recomeçar", "Zoekopdracht wissen en opnieuw beginnen"],
    "Press / to search": ["Pulsa / para buscar", "Appuyez sur / pour rechercher", "Drücke / zum Suchen", "Premi / per cercare", "Pressione / para buscar", "Druk op / om te zoeken"],
    "Menu": ["Menú", "Menu", "Menü", "Menu", "Menu", "Menu"],
    "Main menu": ["Menú principal", "Menu principal", "Hauptmenü", "Menu principale", "Menu principal", "Hoofdmenu"],
    "Language": ["Idioma", "Langue", "Sprache", "Lingua", "Idioma", "Taal"],
    "Home": ["Inicio", "Accueil", "Start", "Home", "Início", "Home"],
    "Back to the start screen": ["Volver a la pantalla de inicio", "Retour à l'écran d'accueil", "Zurück zum Startbildschirm", "Torna alla schermata iniziale", "Voltar para a tela inicial", "Terug naar het startscherm"],
    "Your saved tracks": ["Tus temas guardados", "Vos titres enregistrés", "Deine gespeicherten Tracks", "I tuoi brani salvati", "Suas faixas salvas", "Je opgeslagen tracks"],
    "Artists like…": ["Artistas como…", "Artistes comme…", "Ähnliche Artists…", "Artisti simili…", "Artistas parecidos…", "Artiesten zoals…"],
    "Browse tracks": ["Explorar temas", "Parcourir les titres", "Tracks durchsuchen", "Sfoglia i brani", "Explorar faixas", "Tracks bekijken"],
    "By sub-genre and BPM": ["Por subgénero y BPM", "Par sous-genre et BPM", "Nach Subgenre und BPM", "Per sottogenere e BPM", "Por subgênero e BPM", "Op subgenre en BPM"],
    "How it works": ["Cómo funciona", "Comment ça marche", "So funktioniert's", "Come funziona", "Como funciona", "Zo werkt het"],
    "Three steps to a set that flows": ["Tres pasos para un set que fluye", "Trois étapes pour un set fluide", "Drei Schritte zu einem Set, das fließt", "Tre passi per un set fluido", "Três passos para um set que flui", "Drie stappen naar een set die loopt"],
    "Privacy & terms": ["Privacidad y términos", "Confidentialité et conditions", "Datenschutz & Bedingungen", "Privacy e termini", "Privacidade e termos", "Privacy & voorwaarden"],
    "Privacy, cookies and terms of use": ["Privacidad, cookies y términos de uso", "Confidentialité, cookies et conditions d'utilisation", "Datenschutz, Cookies und Nutzungsbedingungen", "Privacy, cookie e termini d'uso", "Privacidade, cookies e termos de uso", "Privacy, cookies en gebruiksvoorwaarden"],
    "Share SimilarSounds": ["Compartir SimilarSounds", "Partager SimilarSounds", "SimilarSounds teilen", "Condividi SimilarSounds", "Compartilhar SimilarSounds", "SimilarSounds delen"],
    "Copy the site link": ["Copiar el enlace del sitio", "Copier le lien du site", "Website-Link kopieren", "Copia il link del sito", "Copiar o link do site", "Websitelink kopiëren"],
    "SimilarSounds - home": ["SimilarSounds - inicio", "SimilarSounds - accueil", "SimilarSounds - Start", "SimilarSounds - home", "SimilarSounds - início", "SimilarSounds - home"],
    "Your set": ["Tu set", "Votre set", "Dein Set", "Il tuo set", "Seu set", "Je set"],
    "Close": ["Cerrar", "Fermer", "Schließen", "Chiudi", "Fechar", "Sluiten"],
    "Nothing here yet.": ["Aún no hay nada.", "Rien pour l'instant.", "Noch nichts hier.", "Ancora niente qui.", "Nada aqui ainda.", "Nog niets hier."],
    "Energy flow": ["Flujo de energía", "Courbe d'énergie", "Energieverlauf", "Andamento dell'energia", "Fluxo de energia", "Energieverloop"],
    "✦ Smart order": ["✦ Orden inteligente", "✦ Ordre intelligent", "✦ Smarte Reihenfolge", "✦ Ordine intelligente", "✦ Ordem inteligente", "✦ Slimme volgorde"],
    "Reorder for the smoothest mixes and a steady energy build": ["Reordenar para las mezclas más suaves y una subida de energía constante", "Réordonner pour des enchaînements fluides et une montée d'énergie régulière", "Für die geschmeidigsten Übergänge und einen gleichmäßigen Energieaufbau neu ordnen", "Riordina per i mix più fluidi e una crescita costante dell'energia", "Reordenar para as mixagens mais suaves e uma energia crescente", "Herschikken voor de soepelste mixen en een gestage energieopbouw"],
    "Copy tracklist": ["Copiar tracklist", "Copier la tracklist", "Tracklist kopieren", "Copia tracklist", "Copiar tracklist", "Tracklist kopiëren"],
    "Clear set": ["Vaciar set", "Vider le set", "Set leeren", "Svuota set", "Limpar set", "Set legen"],
    "Share your set with others": ["Comparte tu set con otros", "Partagez votre set", "Teile dein Set mit anderen", "Condividi il tuo set con gli altri", "Compartilhe seu set com outras pessoas", "Deel je set met anderen"],
    "Send a link - they'll see your tracks in this order": ["Envía un enlace: verán tus temas en este orden", "Envoyez un lien : ils verront vos titres dans cet ordre", "Schick einen Link – sie sehen deine Tracks in dieser Reihenfolge", "Invia un link: vedranno i tuoi brani in quest'ordine", "Envie um link: verão suas faixas nesta ordem", "Stuur een link – ze zien je tracks in deze volgorde"],
    "Your set is empty": ["Tu set está vacío", "Votre set est vide", "Dein Set ist leer", "Il tuo set è vuoto", "Seu set está vazio", "Je set is leeg"],
    "+ Add tracks": ["+ Añadir temas", "+ Ajouter des titres", "+ Tracks hinzufügen", "+ Aggiungi brani", "+ Adicionar faixas", "+ Tracks toevoegen"],
    "green": ["verde", "vert", "Grün", "verde", "verde", "groen"],
    "amber": ["ámbar", "orange", "Gelb", "giallo", "âmbar", "oranje"],
    "red": ["rojo", "rouge", "Rot", "rosso", "vermelho", "rood"],
    "Find what mixes next →": ["Busca qué mezcla después →", "Trouver le titre suivant →", "Finde, was als Nächstes passt →", "Trova cosa mixare dopo →", "Encontre o que mixar depois →", "Vind wat erna mixt →"],
    "Drag to reorder": ["Arrastra para reordenar", "Glisser pour réordonner", "Zum Neuordnen ziehen", "Trascina per riordinare", "Arraste para reordenar", "Sleep om te herschikken"],
    "Move up": ["Subir", "Monter", "Nach oben", "Sposta su", "Mover para cima", "Omhoog"],
    "Move down": ["Bajar", "Descendre", "Nach unten", "Sposta giù", "Mover para baixo", "Omlaag"],
    "Remove": ["Quitar", "Retirer", "Entfernen", "Rimuovi", "Remover", "Verwijderen"],
    "Your track": ["Tu tema", "Votre titre", "Dein Track", "Il tuo brano", "Sua faixa", "Jouw track"],
    "From YouTube": ["De YouTube", "Depuis YouTube", "Von YouTube", "Da YouTube", "Do YouTube", "Van YouTube"],
    "From SoundCloud": ["De SoundCloud", "Depuis SoundCloud", "Von SoundCloud", "Da SoundCloud", "Do SoundCloud", "Van SoundCloud"],
    "From Bandcamp": ["De Bandcamp", "Depuis Bandcamp", "Von Bandcamp", "Da Bandcamp", "Do Bandcamp", "Van Bandcamp"],
    "Listen on Bandcamp ↗": ["Escuchar en Bandcamp ↗", "Écouter sur Bandcamp ↗", "Auf Bandcamp anhören ↗", "Ascolta su Bandcamp ↗", "Ouvir no Bandcamp ↗", "Luisteren op Bandcamp ↗"],
    "Please paste a Bandcamp *track* link.": ["Pega un enlace de un *tema* de Bandcamp.", "Collez un lien vers un *titre* Bandcamp.", "Bitte füge einen Bandcamp-*Track*-Link ein.", "Incolla il link di un *brano* Bandcamp.", "Cole o link de uma *faixa* do Bandcamp.", "Plak een link naar een Bandcamp-*track*."],
    "From Beatport": ["De Beatport", "Depuis Beatport", "Von Beatport", "Da Beatport", "Do Beatport", "Van Beatport"],
    "Listen on SoundCloud": ["Escuchar en SoundCloud", "Écouter sur SoundCloud", "Auf SoundCloud anhören", "Ascolta su SoundCloud", "Ouvir no SoundCloud", "Luisteren op SoundCloud"],
    "Watch on YouTube": ["Ver en YouTube", "Regarder sur YouTube", "Auf YouTube ansehen", "Guarda su YouTube", "Assistir no YouTube", "Bekijken op YouTube"],
    "Copy link": ["Copiar enlace", "Copier le lien", "Link kopieren", "Copia link", "Copiar link", "Link kopiëren"],
    "Copy a link to these results": ["Copiar un enlace a estos resultados", "Copier un lien vers ces résultats", "Link zu diesen Ergebnissen kopieren", "Copia un link a questi risultati", "Copiar um link para estes resultados", "Link naar deze resultaten kopiëren"],
    "Sort": ["Ordenar", "Trier", "Sortieren", "Ordina", "Ordenar", "Sorteren"],
    "Sort results": ["Ordenar resultados", "Trier les résultats", "Ergebnisse sortieren", "Ordina risultati", "Ordenar resultados", "Resultaten sorteren"],
    "Mixes well first": ["Mezclan bien primero", "Meilleurs enchaînements d'abord", "Passende zuerst", "Prima quelli che si mixano bene", "Mixam bem primeiro", "Goed mixend eerst"],
    "Highest match %": ["Mayor % de parecido", "% de ressemblance le plus élevé", "Höchste Ähnlichkeit %", "% di somiglianza più alta", "Maior % de semelhança", "Hoogste match-%"],
    "Newest": ["Más nuevos", "Plus récents", "Neueste", "Più recenti", "Mais novos", "Nieuwste"],
    "Closest BPM": ["BPM más cercano", "BPM le plus proche", "Nächstes BPM", "BPM più vicino", "BPM mais próximo", "Dichtstbijzijnde BPM"],
    "How to read these results": ["Cómo leer estos resultados", "Comment lire ces résultats", "So liest du diese Ergebnisse", "Come leggere questi risultati", "Como ler estes resultados", "Zo lees je deze resultaten"],
    "Mix from your track": ["Mezcla desde tu tema", "Enchaînement depuis votre titre", "Übergang von deinem Track", "Mix dal tuo brano", "Mix a partir da sua faixa", "Mix vanaf jouw track"],
    "Green mixes well, amber is workable, red will clash. The line says why.": ["Verde mezcla bien, ámbar es aceptable, rojo chocará. La línea explica por qué.", "Vert s'enchaîne bien, orange est jouable, rouge va clasher. La ligne explique pourquoi.", "Grün passt gut, Gelb ist machbar, Rot kollidiert. Die Zeile erklärt warum.", "Verde si mixa bene, giallo è accettabile, rosso stonerà. La riga spiega perché.", "Verde mixa bem, âmbar é aceitável, vermelho vai chocar. A linha explica por quê.", "Groen mixt goed, oranje is werkbaar, rood botst. De regel legt uit waarom."],
    "Key (Camelot)": ["Tonalidad (Camelot)", "Tonalité (Camelot)", "Tonart (Camelot)", "Tonalità (Camelot)", "Tom (Camelot)", "Toonsoort (Camelot)"],
    "Same number or one step away (7A, 9A, 8B) mixes in key.": ["El mismo número o uno al lado (7A, 9A, 8B) mezcla en tonalidad.", "Même numéro ou un cran à côté (7A, 9A, 8B) : ça s'enchaîne dans la tonalité.", "Gleiche Zahl oder ein Schritt daneben (7A, 9A, 8B) mischt harmonisch.", "Stesso numero o uno accanto (7A, 9A, 8B) si mixa in tonalità.", "Mesmo número ou um passo ao lado (7A, 9A, 8B) mixa no tom.", "Hetzelfde nummer of één stap ernaast (7A, 9A, 8B) mixt harmonisch."],
    "Track energy": ["Energía del tema", "Énergie du titre", "Track-Energie", "Energia del brano", "Energia da faixa", "Track-energie"],
    "How hard the track hits, from 1 (deep and chilled) to 10 (peak-time).": ["Lo fuerte que pega el tema, de 1 (profundo y relajado) a 10 (hora punta).", "L'intensité du titre, de 1 (deep et posé) à 10 (peak-time).", "Wie hart der Track reinhaut, von 1 (deep und entspannt) bis 10 (Peak-Time).", "Quanto spinge il brano, da 1 (deep e rilassato) a 10 (peak-time).", "O quanto a faixa bate, de 1 (deep e tranquila) a 10 (pico da pista).", "Hoe hard de track binnenkomt, van 1 (deep en relaxed) tot 10 (peak-time)."],
    "Sound match": ["Parecido sonoro", "Ressemblance sonore", "Sound-Ähnlichkeit", "Somiglianza sonora", "Semelhança sonora", "Soundmatch"],
    "How close it sounds to your track.": ["Cuánto se parece a tu tema.", "À quel point il ressemble à votre titre.", "Wie ähnlich er deinem Track klingt.", "Quanto somiglia al tuo brano.", "O quanto soa parecido com sua faixa.", "Hoe dicht het bij jouw track klinkt."],
    "How close it sounds to your track": ["Cuánto se parece a tu tema", "À quel point il ressemble à votre titre", "Wie ähnlich er deinem Track klingt", "Quanto somiglia al tuo brano", "O quanto soa parecido com sua faixa", "Hoe dicht het bij jouw track klinkt"],
    "Mixes well": ["Mezcla bien", "S'enchaîne bien", "Passt gut", "Si mixa bene", "Mixa bem", "Mixt goed"],
    "Workable": ["Aceptable", "Jouable", "Machbar", "Accettabile", "Aceitável", "Werkbaar"],
    "Will clash": ["Chocará", "Va clasher", "Kollidiert", "Stonerà", "Vai chocar", "Botst"],
    "NEW": ["NUEVO", "NOUVEAU", "NEU", "NUOVO", "NOVO", "NIEUW"],
    "✓ In set": ["✓ En el set", "✓ Dans le set", "✓ Im Set", "✓ Nel set", "✓ No set", "✓ In set"],
    "Find similar →": ["Buscar similares →", "Titres similaires →", "Ähnliche finden →", "Trova simili →", "Buscar parecidas →", "Vergelijkbare vinden →"],
    "Similar →": ["Similares →", "Similaires →", "Ähnliche →", "Simili →", "Parecidas →", "Vergelijkbaar →"],
    "Find tracks similar to this": ["Buscar temas parecidos", "Trouver des titres similaires", "Ähnliche Tracks finden", "Trova brani simili", "Buscar faixas parecidas", "Vergelijkbare tracks vinden"],
    "Also on": ["También en", "Aussi sur", "Auch auf", "Anche su", "Também no", "Ook op"],
    "Show 30 more matches": ["Mostrar 30 más", "Afficher 30 de plus", "30 weitere anzeigen", "Mostra altri 30", "Mostrar mais 30", "Toon nog 30"],
    "Load player": ["Cargar reproductor", "Charger le lecteur", "Player laden", "Carica player", "Carregar player", "Speler laden"],
    "Our cookie policy": ["Nuestra política de cookies", "Notre politique de cookies", "Unsere Cookie-Richtlinie", "La nostra cookie policy", "Nossa política de cookies", "Ons cookiebeleid"],
    "This doesn't look like a house track": ["Esto no parece un tema de house", "Ce titre ne ressemble pas à de la house", "Das klingt nicht nach House", "Questo non sembra un brano house", "Isso não parece uma faixa de house", "Dit lijkt geen housetrack"],
    "Show house matches anyway": ["Mostrar coincidencias de house igualmente", "Afficher quand même des titres house", "Trotzdem House-Treffer zeigen", "Mostra comunque brani house", "Mostrar faixas de house mesmo assim", "Toch housematches tonen"],
    "Not a house track, so these are the closest house tracks we have.": ["No es un tema de house, así que estos son los temas de house más parecidos que tenemos.", "Ce n'est pas de la house, voici donc les titres house les plus proches que nous ayons.", "Kein House-Track – das sind die ähnlichsten House-Tracks, die wir haben.", "Non è un brano house, quindi questi sono i brani house più vicini che abbiamo.", "Não é uma faixa de house, então estas são as faixas de house mais próximas que temos.", "Geen housetrack, dus dit zijn de dichtstbijzijnde housetracks die we hebben."],
    "We couldn't find that track": ["No encontramos ese tema", "Nous n'avons pas trouvé ce titre", "Wir konnten diesen Track nicht finden", "Non abbiamo trovato quel brano", "Não encontramos essa faixa", "We konden die track niet vinden"],
    "artist's name": ["nombre del artista", "nom de l'artiste", "Namen des Artists", "nome dell'artista", "nome do artista", "artiestennaam"],
    "Artist - Title": ["Artista - Título", "Artiste - Titre", "Artist - Titel", "Artista - Titolo", "Artista - Título", "Artiest - Titel"],
    "Brand-new or very underground tracks may not have a preview yet.": ["Los temas recién salidos o muy underground puede que aún no tengan preview.", "Les titres tout juste sortis ou très underground n'ont peut-être pas encore d'extrait.", "Brandneue oder sehr undergroundige Tracks haben vielleicht noch keine Vorschau.", "I brani appena usciti o molto underground potrebbero non avere ancora un'anteprima.", "Faixas recém-lançadas ou muito underground podem ainda não ter prévia.", "Gloednieuwe of heel underground tracks hebben misschien nog geen preview."],
    "That link isn't one we can read yet": ["Todavía no podemos leer ese enlace", "Nous ne pouvons pas encore lire ce lien", "Diesen Link können wir noch nicht lesen", "Non possiamo ancora leggere quel link", "Ainda não conseguimos ler esse link", "Die link kunnen we nog niet lezen"],
    "Can't reach SimilarSounds right now": ["No se puede conectar con SimilarSounds ahora", "Impossible de joindre SimilarSounds pour le moment", "SimilarSounds ist gerade nicht erreichbar", "Impossibile raggiungere SimilarSounds al momento", "Não foi possível acessar o SimilarSounds agora", "SimilarSounds is nu niet bereikbaar"],
    "Check your connection. If the site has been quiet for a while it may be waking up - give it a few seconds.": ["Revisa tu conexión. Si el sitio llevaba un rato sin uso, puede que esté arrancando: dale unos segundos.", "Vérifiez votre connexion. Si le site était inactif depuis un moment, il est peut-être en train de se réveiller : patientez quelques secondes.", "Prüf deine Verbindung. Wenn die Seite eine Weile nicht genutzt wurde, startet sie vielleicht gerade – gib ihr ein paar Sekunden.", "Controlla la connessione. Se il sito era inattivo da un po', potrebbe essere in fase di avvio: attendi qualche secondo.", "Verifique sua conexão. Se o site estava parado há algum tempo, pode estar iniciando: aguarde alguns segundos.", "Controleer je verbinding. Als de site een tijdje stil was, start hij misschien net op – geef hem een paar seconden."],
    "Something went wrong on our side": ["Algo ha fallado por nuestra parte", "Un problème est survenu de notre côté", "Bei uns ist etwas schiefgelaufen", "Qualcosa è andato storto da parte nostra", "Algo deu errado do nosso lado", "Er ging iets mis aan onze kant"],
    "Try again": ["Reintentar", "Réessayer", "Erneut versuchen", "Riprova", "Tentar de novo", "Opnieuw proberen"],
    "Supported links: YouTube, SoundCloud, Beatport, Bandcamp, Deezer - or type 'Artist - Title'.": ["Enlaces compatibles: YouTube, SoundCloud, Beatport, Bandcamp, Deezer, o escribe 'Artista - Título'.", "Liens pris en charge : YouTube, SoundCloud, Beatport, Bandcamp, Deezer, ou tapez « Artiste - Titre ».", "Unterstützte Links: YouTube, SoundCloud, Beatport, Bandcamp, Deezer – oder gib „Artist - Titel“ ein.", "Link supportati: YouTube, SoundCloud, Beatport, Bandcamp, Deezer, oppure scrivi 'Artista - Titolo'.", "Links compatíveis: YouTube, SoundCloud, Beatport, Bandcamp, Deezer, ou digite 'Artista - Título'.", "Ondersteunde links: YouTube, SoundCloud, Beatport, Bandcamp, Deezer – of typ 'Artiest - Titel'."],
    "Please paste a Deezer *track* link.": ["Pega un enlace de un *tema* de Deezer.", "Collez un lien vers un *titre* Deezer.", "Bitte füge einen Deezer-*Track*-Link ein.", "Incolla il link di un *brano* Deezer.", "Cole o link de uma *faixa* do Deezer.", "Plak een link naar een Deezer-*track*."],
    "Please paste a Beatport *track* link.": ["Pega un enlace de un *tema* de Beatport.", "Collez un lien vers un *titre* Beatport.", "Bitte füge einen Beatport-*Track*-Link ein.", "Incolla il link di un *brano* Beatport.", "Cole o link de uma *faixa* do Beatport.", "Plak een link naar een Beatport-*track*."],
    "Couldn't read that YouTube link (is the video public?).": ["No pudimos leer ese enlace de YouTube (¿el vídeo es público?).", "Impossible de lire ce lien YouTube (la vidéo est-elle publique ?).", "Dieser YouTube-Link ließ sich nicht lesen (ist das Video öffentlich?).", "Impossibile leggere quel link YouTube (il video è pubblico?).", "Não foi possível ler esse link do YouTube (o vídeo é público?).", "Die YouTube-link kon niet worden gelezen (is de video openbaar?)."],
    "Couldn't read that SoundCloud link (is the track public?).": ["No pudimos leer ese enlace de SoundCloud (¿el tema es público?).", "Impossible de lire ce lien SoundCloud (le titre est-il public ?).", "Dieser SoundCloud-Link ließ sich nicht lesen (ist der Track öffentlich?).", "Impossibile leggere quel link SoundCloud (il brano è pubblico?).", "Não foi possível ler esse link do SoundCloud (a faixa é pública?).", "Die SoundCloud-link kon niet worden gelezen (is de track openbaar?)."],
    "Finding your track and checking its key, BPM and energy…": ["Buscando tu tema y analizando su tonalidad, BPM y energía…", "Recherche de votre titre et analyse de sa tonalité, de son BPM et de son énergie…", "Dein Track wird gesucht und Tonart, BPM und Energie werden geprüft…", "Cerco il tuo brano e ne controllo tonalità, BPM ed energia…", "Encontrando sua faixa e verificando tom, BPM e energia…", "Je track wordt gezocht en toonsoort, BPM en energie worden gecheckt…"],
    "(new tracks can take ~10 seconds)": ["(los temas nuevos pueden tardar ~10 segundos)", "(les nouveaux titres peuvent prendre ~10 secondes)", "(neue Tracks können ~10 Sekunden dauern)", "(i brani nuovi possono richiedere ~10 secondi)", "(faixas novas podem levar ~10 segundos)", "(nieuwe tracks kunnen ~10 seconden duren)"],
    "Searching…": ["Buscando…", "Recherche…", "Suche…", "Ricerca…", "Buscando…", "Zoeken…"],
    "Artists": ["Artistas", "Artistes", "Artists", "Artisti", "Artistas", "Artiesten"],
    "Artist": ["Artista", "Artiste", "Artist", "Artista", "Artista", "Artiest"],
    "Tracks": ["Temas", "Titres", "Tracks", "Brani", "Faixas", "Tracks"],
    "Recent searches": ["Búsquedas recientes", "Recherches récentes", "Letzte Suchen", "Ricerche recenti", "Buscas recentes", "Recente zoekopdrachten"],
    "Clear": ["Borrar", "Effacer", "Löschen", "Cancella", "Limpar", "Wissen"],
    "No matches yet - keep typing, or press Find.": ["Aún no hay coincidencias: sigue escribiendo o pulsa Buscar.", "Pas encore de résultats : continuez à taper ou appuyez sur Rechercher.", "Noch keine Treffer – tipp weiter oder drück auf Suchen.", "Nessun risultato per ora: continua a scrivere o premi Cerca.", "Nenhum resultado ainda: continue digitando ou toque em Buscar.", "Nog geen resultaten – typ verder of druk op Zoeken."],
    "No matches with these filters - try a wider release window or BPM range.": ["No hay coincidencias con estos filtros: prueba un periodo de lanzamiento o un rango de BPM más amplio.", "Aucun résultat avec ces filtres : élargissez la période de sortie ou la plage de BPM.", "Keine Treffer mit diesen Filtern – probier einen größeren Zeitraum oder BPM-Bereich.", "Nessun risultato con questi filtri: prova un periodo di uscita o un intervallo BPM più ampio.", "Nenhum resultado com esses filtros: tente um período de lançamento ou uma faixa de BPM maior.", "Geen matches met deze filters – probeer een ruimer releasevenster of BPM-bereik."],
    "New search": ["Nueva búsqueda", "Nouvelle recherche", "Neue Suche", "Nuova ricerca", "Nova busca", "Nieuwe zoekopdracht"],
    "Removed from your set": ["Quitado de tu set", "Retiré de votre set", "Aus deinem Set entfernt", "Rimosso dal tuo set", "Removido do seu set", "Uit je set verwijderd"],
    "Undo": ["Deshacer", "Annuler", "Rückgängig", "Annulla", "Desfazer", "Ongedaan maken"],
    "Reordered for smoother mixes": ["Reordenado para mezclas más suaves", "Réordonné pour des enchaînements plus fluides", "Für geschmeidigere Übergänge neu geordnet", "Riordinato per mix più fluidi", "Reordenado para mixagens mais suaves", "Herschikt voor soepelere mixen"],
    "Already in the smoothest order": ["Ya está en el orden más suave", "Déjà dans l'ordre le plus fluide", "Schon in der geschmeidigsten Reihenfolge", "Già nell'ordine più fluido", "Já está na ordem mais suave", "Staat al in de soepelste volgorde"],
    "Add at least 3 tracks to sort them": ["Añade al menos 3 temas para ordenarlos", "Ajoutez au moins 3 titres pour les trier", "Füg mindestens 3 Tracks hinzu, um sie zu sortieren", "Aggiungi almeno 3 brani per ordinarli", "Adicione pelo menos 3 faixas para ordená-las", "Voeg minstens 3 tracks toe om ze te sorteren"],
    "Tracklist copied": ["Tracklist copiada", "Tracklist copiée", "Tracklist kopiert", "Tracklist copiata", "Tracklist copiada", "Tracklist gekopieerd"],
    "Couldn't copy - your browser blocked it": ["No se pudo copiar: tu navegador lo bloqueó", "Copie impossible : votre navigateur l'a bloquée", "Kopieren nicht möglich – dein Browser hat es blockiert", "Impossibile copiare: il browser l'ha bloccato", "Não foi possível copiar: seu navegador bloqueou", "Kopiëren mislukt – je browser blokkeerde het"],
    "Link copied - share these results": ["Enlace copiado: comparte estos resultados", "Lien copié : partagez ces résultats", "Link kopiert – teile diese Ergebnisse", "Link copiato: condividi questi risultati", "Link copiado: compartilhe estes resultados", "Link gekopieerd – deel deze resultaten"],
    "Set link copied - paste it anywhere to share": ["Enlace del set copiado: pégalo donde quieras para compartirlo", "Lien du set copié : collez-le où vous voulez", "Set-Link kopiert – füg ihn zum Teilen überall ein", "Link del set copiato: incollalo dove vuoi per condividerlo", "Link do set copiado: cole onde quiser para compartilhar", "Setlink gekopieerd – plak hem waar je wilt om te delen"],
    "Add some tracks to your set first": ["Primero añade algunos temas a tu set", "Ajoutez d'abord quelques titres à votre set", "Füg zuerst ein paar Tracks zu deinem Set hinzu", "Prima aggiungi qualche brano al tuo set", "Primeiro adicione algumas faixas ao seu set", "Voeg eerst wat tracks toe aan je set"],
    "Site link copied - www.similarsounds.com": ["Enlace del sitio copiado: www.similarsounds.com", "Lien du site copié : www.similarsounds.com", "Website-Link kopiert – www.similarsounds.com", "Link del sito copiato: www.similarsounds.com", "Link do site copiado: www.similarsounds.com", "Websitelink gekopieerd – www.similarsounds.com"],
    "Recent searches cleared": ["Búsquedas recientes borradas", "Recherches récentes effacées", "Letzte Suchen gelöscht", "Ricerche recenti cancellate", "Buscas recentes apagadas", "Recente zoekopdrachten gewist"],
    "Opening the shared set…": ["Abriendo el set compartido…", "Ouverture du set partagé…", "Geteiltes Set wird geöffnet…", "Apertura del set condiviso…", "Abrindo o set compartilhado…", "Gedeelde set openen…"],
    "Keep mine": ["Quedarme con el mío", "Garder le mien", "Meins behalten", "Tieni il mio", "Manter o meu", "Mijn set houden"],
    "Couldn't open that set": ["No se pudo abrir ese set", "Impossible d'ouvrir ce set", "Dieses Set konnte nicht geöffnet werden", "Impossibile aprire quel set", "Não foi possível abrir esse set", "Die set kon niet worden geopend"],
    "no clashes": ["sin choques", "aucun clash", "keine Kollisionen", "nessun conflitto", "sem choques", "geen botsingen"],
    "Open ›": ["Abrir ›", "Ouvrir ›", "Öffnen ›", "Apri ›", "Abrir ›", "Openen ›"],
    "Clear your whole set": ["Vaciar todo tu set", "Vider tout votre set", "Ganzes Set leeren", "Svuota tutto il set", "Limpar todo o set", "Je hele set legen"],
    "Same key": ["Misma tonalidad", "Même tonalité", "Gleiche Tonart", "Stessa tonalità", "Mesmo tom", "Zelfde toonsoort"],
    "Adjacent key": ["Tonalidad adyacente", "Tonalité voisine", "Benachbarte Tonart", "Tonalità adiacente", "Tom adjacente", "Naastgelegen toonsoort"],
    "Relative major/minor": ["Relativa mayor/menor", "Relatif majeur/mineur", "Paralleltonart", "Relativa maggiore/minore", "Relativo maior/menor", "Parallelle majeur/mineur"],
    "Energy-boost key change (+2)": ["Cambio de tonalidad para subir energía (+2)", "Changement de tonalité énergisant (+2)", "Energie-Boost-Tonartwechsel (+2)", "Cambio di tonalità per alzare l'energia (+2)", "Mudança de tom para subir a energia (+2)", "Energieboost-toonsoortwissel (+2)"],
    "Key change (−2)": ["Cambio de tonalidad (−2)", "Changement de tonalité (−2)", "Tonartwechsel (−2)", "Cambio di tonalità (−2)", "Mudança de tom (−2)", "Toonsoortwissel (−2)"],
    "Diagonal key change": ["Cambio diagonal de tonalidad", "Changement de tonalité en diagonale", "Diagonaler Tonartwechsel", "Cambio di tonalità in diagonale", "Mudança diagonal de tom", "Diagonale toonsoortwissel"],
    "Key clash": ["Choque de tonalidad", "Clash de tonalité", "Tonart-Kollision", "Conflitto di tonalità", "Choque de tom", "Toonsoortbotsing"],
    "same BPM": ["mismo BPM", "même BPM", "gleiches BPM", "stesso BPM", "mesmo BPM", "zelfde BPM"],
    "same energy": ["misma energía", "même énergie", "gleiche Energie", "stessa energia", "mesma energia", "zelfde energie"],
    "today": ["hoy", "aujourd'hui", "heute", "oggi", "hoje", "vandaag"],
    "Privacy Policy": ["Política de privacidad", "Politique de confidentialité", "Datenschutzerklärung", "Informativa sulla privacy", "Política de privacidade", "Privacybeleid"],
    "Cookie Policy": ["Política de cookies", "Politique de cookies", "Cookie-Richtlinie", "Cookie policy", "Política de cookies", "Cookiebeleid"],
    "Terms of Use": ["Términos de uso", "Conditions d'utilisation", "Nutzungsbedingungen", "Termini d'uso", "Termos de uso", "Gebruiksvoorwaarden"],
    "Contact": ["Contacto", "Contact", "Kontakt", "Contatti", "Contato", "Contact"],
    "Legal": ["Legal", "Mentions légales", "Rechtliches", "Note legali", "Jurídico", "Juridisch"],
    "SimilarSounds is in early preview. Previews and track details by Deezer; players from SoundCloud and YouTube load only when you choose. Key, BPM and energy are estimates, so always trust your ears. Not affiliated with Deezer, SoundCloud, YouTube or Beatport.": [
      "SimilarSounds está en versión preliminar. Previews y datos de los temas por Deezer; los reproductores de SoundCloud y YouTube solo se cargan cuando tú lo eliges. La tonalidad, el BPM y la energía son estimaciones, así que fíate siempre de tus oídos. Sin relación con Deezer, SoundCloud, YouTube ni Beatport.",
      "SimilarSounds est en avant-première. Extraits et infos des titres par Deezer ; les lecteurs SoundCloud et YouTube ne se chargent que si vous le choisissez. Tonalité, BPM et énergie sont des estimations : fiez-vous toujours à vos oreilles. Non affilié à Deezer, SoundCloud, YouTube ou Beatport.",
      "SimilarSounds ist eine frühe Vorschau. Vorschauen und Track-Infos von Deezer; Player von SoundCloud und YouTube laden nur, wenn du es willst. Tonart, BPM und Energie sind Schätzungen – vertrau immer deinen Ohren. Nicht verbunden mit Deezer, SoundCloud, YouTube oder Beatport.",
      "SimilarSounds è in anteprima. Anteprime e dati dei brani da Deezer; i player di SoundCloud e YouTube si caricano solo quando lo scegli. Tonalità, BPM ed energia sono stime: fidati sempre delle tue orecchie. Non affiliato a Deezer, SoundCloud, YouTube o Beatport.",
      "O SimilarSounds está em prévia. Prévias e dados das faixas pela Deezer; os players do SoundCloud e do YouTube só carregam quando você escolhe. Tom, BPM e energia são estimativas, então confie sempre nos seus ouvidos. Sem afiliação com Deezer, SoundCloud, YouTube ou Beatport.",
      "SimilarSounds is een vroege preview. Previews en trackgegevens via Deezer; spelers van SoundCloud en YouTube laden alleen als jij dat kiest. Toonsoort, BPM en energie zijn schattingen, dus vertrouw altijd op je oren. Niet gelieerd aan Deezer, SoundCloud, YouTube of Beatport."],
    "Give us a review": ["Danos tu opinión", "Donnez-nous votre avis", "Bewerte uns", "Lasciaci una recensione", "Deixe sua avaliação", "Geef ons een review"],
    "Thank you!": ["¡Gracias!", "Merci !", "Danke!", "Grazie!", "Obrigado!", "Bedankt!"],
    "1 star": ["1 estrella", "1 étoile", "1 Stern", "1 stella", "1 estrela", "1 ster"],
    "Questions": ["Preguntas", "Questions", "Fragen", "Domande", "Perguntas", "Vragen"],
    "What is SimilarSounds?": ["¿Qué es SimilarSounds?", "Qu'est-ce que SimilarSounds ?", "Was ist SimilarSounds?", "Che cos'è SimilarSounds?", "O que é o SimilarSounds?", "Wat is SimilarSounds?"],
    "A free tool for DJs. Paste a track and it finds new house music that sounds like it and mixes with it, newest releases first.": ["Una herramienta gratuita para DJs. Pega un tema y encuentra música house nueva que suena parecida y mezcla con él, empezando por los lanzamientos más recientes.", "Un outil gratuit pour les DJs. Collez un titre et il trouve de la house récente qui sonne pareil et s'enchaîne avec, en commençant par les dernières sorties.", "Ein kostenloses Tool für DJs. Füge einen Track ein und es findet neue House-Musik, die ähnlich klingt und dazu passt – neueste Releases zuerst.", "Uno strumento gratuito per DJ. Incolla un brano e trova nuova musica house che suona simile e si mixa con esso, partendo dalle uscite più recenti.", "Uma ferramenta gratuita para DJs. Cole uma faixa e ela encontra house music nova que soa parecida e mixa com ela, começando pelos lançamentos mais recentes.", "Een gratis tool voor DJ's. Plak een track en hij vindt nieuwe housemuziek die erop lijkt en ermee mixt, nieuwste releases eerst."],
    "How does it decide what mixes?": ["¿Cómo decide qué mezcla bien?", "Comment décide-t-il de ce qui s'enchaîne ?", "Wie entscheidet es, was passt?", "Come decide cosa si mixa?", "Como ele decide o que mixa?", "Hoe bepaalt het wat mixt?"],
    "Every track is analysed for its sound, musical key (shown in Camelot, like 8A), BPM and energy. Matches are ranked by how close they sound, then checked for key, tempo and energy so you can see at a glance what will blend.": ["Cada tema se analiza por su sonido, tonalidad (en Camelot, como 8A), BPM y energía. Las coincidencias se ordenan por parecido sonoro y luego se comprueban tonalidad, tempo y energía para que veas de un vistazo qué va a encajar.", "Chaque titre est analysé pour son son, sa tonalité (en Camelot, comme 8A), son BPM et son énergie. Les résultats sont classés selon leur ressemblance, puis vérifiés en tonalité, tempo et énergie pour voir d'un coup d'œil ce qui s'enchaîne.", "Jeder Track wird auf Sound, Tonart (in Camelot, z. B. 8A), BPM und Energie analysiert. Treffer werden nach Klangähnlichkeit sortiert und dann auf Tonart, Tempo und Energie geprüft, damit du sofort siehst, was passt.", "Ogni brano viene analizzato per suono, tonalità (in Camelot, come 8A), BPM ed energia. I risultati sono ordinati per somiglianza sonora e poi verificati per tonalità, tempo ed energia, così vedi subito cosa si mixa.", "Cada faixa é analisada pelo som, tom (em Camelot, como 8A), BPM e energia. Os resultados são ordenados pela semelhança e depois conferidos em tom, andamento e energia, para você ver na hora o que vai combinar.", "Elke track wordt geanalyseerd op sound, toonsoort (in Camelot, zoals 8A), BPM en energie. Matches worden gerangschikt op hoe dichtbij ze klinken en daarna gecheckt op toonsoort, tempo en energie, zodat je meteen ziet wat blendt."],
    "What can I paste in?": ["¿Qué puedo pegar?", "Que puis-je coller ?", "Was kann ich einfügen?", "Cosa posso incollare?", "O que posso colar?", "Wat kan ik plakken?"],
    "A YouTube, SoundCloud, Beatport, Bandcamp or Deezer link, or just start typing an artist and pick the track from the list.": ["Un enlace de YouTube, SoundCloud, Beatport, Bandcamp o Deezer, o empieza a escribir un artista y elige el tema de la lista.", "Un lien YouTube, SoundCloud, Beatport, Bandcamp ou Deezer, ou commencez à taper un artiste et choisissez le titre dans la liste.", "Einen YouTube-, SoundCloud-, Beatport, Bandcamp- oder Deezer-Link – oder fang an, einen Artist einzugeben, und wähl den Track aus der Liste.", "Un link di YouTube, SoundCloud, Beatport, Bandcamp o Deezer, oppure inizia a scrivere un artista e scegli il brano dall'elenco.", "Um link do YouTube, SoundCloud, Beatport, Bandcamp ou Deezer, ou comece a digitar um artista e escolha a faixa na lista.", "Een YouTube-, SoundCloud-, Beatport, Bandcamp- of Deezer-link, of begin een artiest te typen en kies de track uit de lijst."],
    "Is it free? Do I need an account?": ["¿Es gratis? ¿Necesito una cuenta?", "C'est gratuit ? Faut-il un compte ?", "Ist es kostenlos? Brauche ich ein Konto?", "È gratis? Serve un account?", "É grátis? Preciso de uma conta?", "Is het gratis? Heb ik een account nodig?"],
    "It's completely free, with no account, no ads and no tracking. Your set and recent searches are saved only on your own device.": ["Es totalmente gratis, sin cuenta, sin anuncios y sin rastreo. Tu set y tus búsquedas recientes se guardan solo en tu dispositivo.", "C'est entièrement gratuit, sans compte, sans pub et sans pistage. Votre set et vos recherches récentes restent uniquement sur votre appareil.", "Komplett kostenlos, ohne Konto, ohne Werbung und ohne Tracking. Dein Set und deine letzten Suchen werden nur auf deinem Gerät gespeichert.", "È completamente gratuito, senza account, senza pubblicità e senza tracciamento. Il tuo set e le ricerche recenti restano solo sul tuo dispositivo.", "É totalmente grátis, sem conta, sem anúncios e sem rastreamento. Seu set e suas buscas recentes ficam salvos só no seu aparelho.", "Het is helemaal gratis, zonder account, zonder advertenties en zonder tracking. Je set en recente zoekopdrachten worden alleen op je eigen apparaat bewaard."],
    "Why only house music?": ["¿Por qué solo house?", "Pourquoi seulement de la house ?", "Warum nur House?", "Perché solo house?", "Por que só house?", "Waarom alleen house?"],
    "Doing one genre properly beats doing everything badly. Every track in the catalogue is house, from deep and organic to tech, afro and bass house, so matches stay usable in a house set.": ["Hacer bien un género es mejor que hacerlo todo mal. Todos los temas del catálogo son house, del deep y orgánico al tech, afro y bass house, así que las coincidencias sirven en un set de house.", "Bien faire un seul genre vaut mieux que tout faire à moitié. Tous les titres du catalogue sont de la house, du deep et de l'organic à la tech, l'afro et la bass house, pour des résultats jouables dans un set house.", "Ein Genre richtig zu machen ist besser, als alles halb. Jeder Track im Katalog ist House – von Deep und Organic bis Tech, Afro und Bass House –, damit die Treffer in ein House-Set passen.", "Fare bene un solo genere è meglio che fare tutto male. Ogni brano del catalogo è house, dalla deep e organic alla tech, afro e bass house, così i risultati funzionano in un set house.", "Fazer um gênero bem é melhor do que fazer tudo mal. Todas as faixas do catálogo são house, do deep e orgânico ao tech, afro e bass house, então os resultados funcionam num set de house.", "Eén genre goed doen is beter dan alles half. Elke track in de catalogus is house, van deep en organic tot tech, afro en bass house, zodat de matches bruikbaar blijven in een houseset."],
    "How accurate are the key and BPM?": ["¿Qué precisión tienen la tonalidad y el BPM?", "Quelle est la précision de la tonalité et du BPM ?", "Wie genau sind Tonart und BPM?", "Quanto sono precisi tonalità e BPM?", "Qual a precisão do tom e do BPM?", "Hoe nauwkeurig zijn toonsoort en BPM?"],
    "They're worked out automatically from 30-second previews, so they're good estimates rather than guarantees. Always trust your ears before you mix.": ["Se calculan automáticamente a partir de previews de 30 segundos, así que son buenas estimaciones, no garantías. Fíate siempre de tus oídos antes de mezclar.", "Ils sont calculés automatiquement à partir d'extraits de 30 secondes : ce sont de bonnes estimations, pas des garanties. Fiez-vous toujours à vos oreilles avant de mixer.", "Sie werden automatisch aus 30-Sekunden-Vorschauen ermittelt – gute Schätzungen, aber keine Garantie. Vertrau vor dem Mixen immer deinen Ohren.", "Sono calcolati automaticamente da anteprime di 30 secondi, quindi sono buone stime, non garanzie. Fidati sempre delle tue orecchie prima di mixare.", "São calculados automaticamente a partir de prévias de 30 segundos, então são boas estimativas, não garantias. Confie sempre nos seus ouvidos antes de mixar.", "Ze worden automatisch bepaald uit previews van 30 seconden, dus het zijn goede schattingen, geen garanties. Vertrouw altijd op je oren voordat je mixt."],
    "Can I download the tracks?": ["¿Puedo descargar los temas?", "Puis-je télécharger les titres ?", "Kann ich die Tracks herunterladen?", "Posso scaricare i brani?", "Posso baixar as faixas?", "Kan ik de tracks downloaden?"],
    "No. SimilarSounds doesn't host or sell music. Each match links to Beatport, SoundCloud and YouTube so you can buy or stream it from the artist.": ["No. SimilarSounds no aloja ni vende música. Cada coincidencia enlaza a Beatport, SoundCloud y YouTube para que la compres o escuches desde el artista.", "Non. SimilarSounds n'héberge ni ne vend de musique. Chaque titre renvoie vers Beatport, SoundCloud et YouTube pour l'acheter ou l'écouter auprès de l'artiste.", "Nein. SimilarSounds hostet und verkauft keine Musik. Jeder Treffer verlinkt zu Beatport, SoundCloud und YouTube, damit du ihn beim Artist kaufen oder streamen kannst.", "No. SimilarSounds non ospita né vende musica. Ogni risultato rimanda a Beatport, SoundCloud e YouTube per acquistarlo o ascoltarlo dall'artista.", "Não. O SimilarSounds não hospeda nem vende música. Cada resultado leva ao Beatport, SoundCloud e YouTube para você comprar ou ouvir direto do artista.", "Nee. SimilarSounds host of verkoopt geen muziek. Elke match linkt naar Beatport, SoundCloud en YouTube, zodat je hem bij de artiest kunt kopen of streamen."],
    "How do I build a set?": ["¿Cómo armo un set?", "Comment construire un set ?", "Wie stelle ich ein Set zusammen?", "Come creo un set?", "Como monto um set?", "Hoe bouw ik een set?"],
    "Tap + Set on any track you like, then open Your set. Drag tracks into order or press Smart order, and every transition is coloured green, amber or red so you can spot clashes. Share the set with a link.": ["Toca + Set en los temas que te gusten y abre Tu set. Arrástralos para ordenarlos o pulsa Orden inteligente: cada transición se colorea en verde, ámbar o rojo para detectar choques. Comparte el set con un enlace.", "Touchez + Set sur les titres qui vous plaisent, puis ouvrez Votre set. Faites-les glisser ou appuyez sur Ordre intelligent : chaque transition est colorée en vert, orange ou rouge pour repérer les clashs. Partagez le set avec un lien.", "Tippe bei Tracks, die dir gefallen, auf + Set und öffne dann Dein Set. Zieh sie in die richtige Reihenfolge oder drück Smarte Reihenfolge – jeder Übergang wird grün, gelb oder rot markiert. Teile das Set per Link.", "Tocca + Set sui brani che ti piacciono, poi apri Il tuo set. Trascinali in ordine o premi Ordine intelligente: ogni passaggio è colorato di verde, giallo o rosso per vedere i conflitti. Condividi il set con un link.", "Toque em + Set nas faixas que você gostar e abra Seu set. Arraste para ordenar ou toque em Ordem inteligente: cada transição fica verde, âmbar ou vermelha para você ver os choques. Compartilhe o set com um link.", "Tik op + Set bij tracks die je goed vindt en open Je set. Sleep ze op volgorde of druk op Slimme volgorde: elke overgang wordt groen, oranje of rood, zodat je botsingen ziet. Deel de set met een link."],
    "These pages are only available in English.": ["Estas páginas solo están disponibles en inglés.", "Ces pages ne sont disponibles qu'en anglais.", "Diese Seiten gibt es nur auf Englisch.", "Queste pagine sono disponibili solo in inglese.", "Estas páginas estão disponíveis apenas em inglês.", "Deze pagina's zijn alleen in het Engels beschikbaar."],
  };

  // ---------- HTML fragments with inner elements kept in place ({1}, {2}… = the original child elements)
  const H = {
    hero2: ["Descubre {1} en música house, con la mezcla perfecta.", "Découvrez {1} house music, avec le mix parfait.", "Hol dir {1} House-Musik, mit dem perfekten Mix.", "Scopri {1} musica house, con il mix perfetto.", "Descubra {1} em house music, com a mixagem perfeita.", "Krijg {1} housemuziek, met de perfecte mix."],
    emptySet: ["Busca un tema, toca {1} en los que te gusten y arrástralos para ordenarlos.", "Cherchez un titre, touchez {1} sur ceux qui vous plaisent et faites-les glisser dans l'ordre.", "Such einen Track, tippe bei den gewünschten auf {1} und zieh sie in die richtige Reihenfolge.", "Cerca un brano, tocca {1} su quelli che ti piacciono e trascinali in ordine.", "Busque uma faixa, toque em {1} nas que você gostar e arraste-as para ordenar.", "Zoek een track, tik op {1} bij de tracks die je leuk vindt en sleep ze op volgorde."],
    colourKey: ["Cada par recibe un color: {1} mezcla bien, {2} es aceptable, {3} chocará.", "Chaque paire a une couleur : {1} s'enchaîne bien, {2} est jouable, {3} va clasher.", "Jedes Paar bekommt eine Farbe: {1} passt gut, {2} ist machbar, {3} kollidiert.", "Ogni coppia ha un colore: {1} si mixa bene, {2} è accettabile, {3} stonerà.", "Cada par recebe uma cor: {1} mixa bem, {2} é aceitável, {3} vai chocar.", "Elk paar krijgt een kleur: {1} mixt goed, {2} is werkbaar, {3} botst."],
    gate: ["Esto carga el reproductor de {1}, que puede usar sus propias cookies. {2} · {3}", "Ceci charge le lecteur de {1}, qui peut déposer ses propres cookies. {2} · {3}", "Hier wird der Player von {1} geladen, der eigene Cookies setzen kann. {2} · {3}", "Questo carica il player di {1}, che può impostare i propri cookie. {2} · {3}", "Isto carrega o player do {1}, que pode definir seus próprios cookies. {2} · {3}", "Dit laadt de speler van {1}, die eigen cookies kan plaatsen. {2} · {3}"],
    uploaded: ["Subido por {1} en", "Mis en ligne par {1} sur", "Hochgeladen von {1} auf", "Caricato da {1} su", "Enviado por {1} no", "Geüpload door {1} op"],
    videofrom: ["Vídeo de {1} en", "Vidéo de {1} sur", "Video von {1} auf", "Video di {1} su", "Vídeo de {1} no", "Video van {1} op"],
    sharedNote: ["Estás viendo una búsqueda compartida de {1}.", "Vous consultez une recherche partagée pour {1}.", "Du siehst eine geteilte Suche für {1}.", "Stai guardando una ricerca condivisa per {1}.", "Você está vendo uma busca compartilhada de {1}.", "Je bekijkt een gedeelde zoekopdracht voor {1}."],
    tip1: ["Empieza a escribir el {1} y elige el tema de la lista: es lo más fiable.", "Commencez à taper le {1} et choisissez le titre dans la liste : c'est le plus fiable.", "Fang an, den {1} einzugeben, und wähl den Track aus der Liste – das ist am zuverlässigsten.", "Inizia a scrivere il {1} e scegli il brano dall'elenco: è il modo più affidabile.", "Comece a digitar o {1} e escolha a faixa na lista: é o jeito mais confiável.", "Begin met het typen van de {1} en kies de track uit de lijst – dat werkt het best."],
    tip2: ["Revisa la ortografía o usa el formato {1}.", "Vérifiez l'orthographe ou utilisez le format {1}.", "Prüf die Schreibweise oder nutze das Format {1}.", "Controlla l'ortografia o usa il formato {1}.", "Confira a grafia ou use o formato {1}.", "Controleer de spelling of gebruik het formaat {1}."],
  };

  // ---------- patterns for text that contains numbers or names ($1, $2 … = captured parts)
  const P = [
    [/^1 track$/, ["1 tema", "1 titre", "1 Track", "1 brano", "1 faixa", "1 track"]],
    [/^(\d+) tracks? · (\d+) smooth, (\d+) workable, (\d+) clashing$/, ["$1 temas · $2 suaves, $3 aceptables, $4 chocan", "$1 titres · $2 fluides, $3 jouables, $4 en clash", "$1 Tracks · $2 geschmeidig, $3 machbar, $4 kollidierend", "$1 brani · $2 fluidi, $3 accettabili, $4 in conflitto", "$1 faixas · $2 suaves, $3 aceitáveis, $4 em choque", "$1 tracks · $2 soepel, $3 werkbaar, $4 botsend"]],
    [/^(\d) stars$/, ["$1 estrellas", "$1 étoiles", "$1 Sterne", "$1 stelle", "$1 estrelas", "$1 sterren"]],
    [/^(\d+) tracks$/, ["$1 temas", "$1 titres", "$1 Tracks", "$1 brani", "$1 faixas", "$1 tracks"]],
    [/^([\d,]+) tracks · ([\d,]+) from the last 12 months$/, ["$1 temas · $2 del último año", "$1 titres · $2 des 12 derniers mois", "$1 Tracks · $2 aus den letzten 12 Monaten", "$1 brani · $2 degli ultimi 12 mesi", "$1 faixas · $2 dos últimos 12 meses", "$1 tracks · $2 van de afgelopen 12 maanden"]],
    [/^(\d+) matches for (.+)$/, ["$1 coincidencias para $2", "$1 résultats pour $2", "$1 Treffer für $2", "$1 risultati per $2", "$1 resultados para $2", "$1 matches voor $2"]],
    [/^(\d+) matches$/, ["$1 coincidencias", "$1 résultats", "$1 Treffer", "$1 risultati", "$1 resultados", "$1 matches"]],
    [/^(\d+) tracks? saved$/, ["$1 temas guardados", "$1 titres enregistrés", "$1 Tracks gespeichert", "$1 brani salvati", "$1 faixas salvas", "$1 tracks opgeslagen"]],
    [/^(\d+) tracks? in our house catalogue$/, ["$1 temas en nuestro catálogo house", "$1 titres dans notre catalogue house", "$1 Tracks in unserem House-Katalog", "$1 brani nel nostro catalogo house", "$1 faixas no nosso catálogo de house", "$1 tracks in onze housecatalogus"]],
    [/^(\d+)% match$/, ["$1% de parecido", "$1% de ressemblance", "$1% ähnlich", "$1% simile", "$1% parecido", "$1% match"]],
    [/^(\d+)d ago$/, ["hace $1 d", "il y a $1 j", "vor $1 T.", "$1 g fa", "há $1 d", "$1 d geleden"]],
    [/^(\d+)mo ago$/, ["hace $1 m", "il y a $1 mois", "vor $1 Mon.", "$1 mesi fa", "há $1 m", "$1 mnd geleden"]],
    [/^([\d.]+)y ago$/, ["hace $1 a", "il y a $1 an", "vor $1 J.", "$1 anni fa", "há $1 a", "$1 jr geleden"]],
    [/^Added to your set \((\d+)\)$/, ["Añadido a tu set ($1)", "Ajouté à votre set ($1)", "Zu deinem Set hinzugefügt ($1)", "Aggiunto al tuo set ($1)", "Adicionado ao seu set ($1)", "Toegevoegd aan je set ($1)"]],
    [/^Set cleared \((\d+) tracks?\)$/, ["Set vaciado ($1 temas)", "Set vidé ($1 titres)", "Set geleert ($1 Tracks)", "Set svuotato ($1 brani)", "Set limpo ($1 faixas)", "Set geleegd ($1 tracks)"]],
    [/^Opened a shared set \((\d+) tracks?\)$/, ["Set compartido abierto ($1 temas)", "Set partagé ouvert ($1 titres)", "Geteiltes Set geöffnet ($1 Tracks)", "Set condiviso aperto ($1 brani)", "Set compartilhado aberto ($1 faixas)", "Gedeelde set geopend ($1 tracks)"]],
    [/^(\d+) clash(?:es)?$/, ["$1 choque(s)", "$1 clash(s)", "$1 Kollision(en)", "$1 conflitto/i", "$1 choque(s)", "$1 botsing(en)"]],
    [/^Tracks by (.+)$/, ["Temas de $1", "Titres de $1", "Tracks von $1", "Brani di $1", "Faixas de $1", "Tracks van $1"]],
    [/^No matching tracks by (.+) - press Find to search anyway\.$/, ["No hay temas de $1 que coincidan; pulsa Buscar para buscar igualmente.", "Aucun titre de $1 ne correspond : appuyez sur Rechercher pour chercher quand même.", "Keine passenden Tracks von $1 – drück auf Suchen, um trotzdem zu suchen.", "Nessun brano di $1 corrisponde: premi Cerca per cercare comunque.", "Nenhuma faixa de $1 encontrada; toque em Buscar para buscar mesmo assim.", "Geen passende tracks van $1 – druk op Zoeken om toch te zoeken."]],
    [/^We couldn't find "(.+)"$/, ["No encontramos \"$1\"", "Nous n'avons pas trouvé « $1 »", "Wir konnten „$1“ nicht finden", "Non abbiamo trovato \"$1\"", "Não encontramos \"$1\"", "We konden \"$1\" niet vinden"]],
    [/^(.+) cookie info ↗$/, ["Info de cookies de $1 ↗", "Cookies de $1 ↗", "Cookie-Infos von $1 ↗", "Info cookie di $1 ↗", "Cookies do $1 ↗", "Cookie-info van $1 ↗"]],
    [/^Always allow (.+) players$/, ["Permitir siempre los reproductores de $1", "Toujours autoriser les lecteurs $1", "$1-Player immer erlauben", "Consenti sempre i player di $1", "Sempre permitir players do $1", "$1-spelers altijd toestaan"]],
    [/^Released (\d{4}-\d{2}-\d{2})$/, ["Lanzado el $1", "Sorti le $1", "Veröffentlicht am $1", "Uscito il $1", "Lançado em $1", "Uitgebracht op $1"]],
    [/^Track energy (\d+) out of 10 \(1 = deep and chilled, 10 = peak-time\)$/, ["Energía del tema $1 de 10 (1 = profundo y relajado, 10 = hora punta)", "Énergie du titre $1 sur 10 (1 = deep et posé, 10 = peak-time)", "Track-Energie $1 von 10 (1 = deep und entspannt, 10 = Peak-Time)", "Energia del brano $1 su 10 (1 = deep e rilassato, 10 = peak-time)", "Energia da faixa $1 de 10 (1 = deep e tranquila, 10 = pico da pista)", "Track-energie $1 van 10 (1 = deep en relaxed, 10 = peak-time)"]],
    [/^Energy across the set, from (\d+) to (\d+)$/, ["Energía a lo largo del set, de $1 a $2", "Énergie sur l'ensemble du set, de $1 à $2", "Energie über das Set, von $1 bis $2", "Energia lungo il set, da $1 a $2", "Energia ao longo do set, de $1 a $2", "Energie over de set, van $1 tot $2"]],
    [/^Preview (.+) by (.+)$/, ["Escuchar $1 de $2", "Écouter $1 de $2", "$1 von $2 anhören", "Ascolta $1 di $2", "Ouvir $1 de $2", "$1 van $2 beluisteren"]],
    [/^Find tracks similar to (.+) by (.+)$/, ["Buscar temas parecidos a $1 de $2", "Trouver des titres similaires à $1 de $2", "Ähnliche Tracks wie $1 von $2 finden", "Trova brani simili a $1 di $2", "Buscar faixas parecidas com $1 de $2", "Tracks vinden die lijken op $1 van $2"]],
    [/^(.+) - similar house tracks \| SimilarSounds$/, ["$1 - temas house parecidos | SimilarSounds", "$1 - titres house similaires | SimilarSounds", "$1 - ähnliche House-Tracks | SimilarSounds", "$1 - brani house simili | SimilarSounds", "$1 - faixas de house parecidas | SimilarSounds", "$1 - vergelijkbare housetracks | SimilarSounds"]],
    // results summary
    [/^Artists that sound like (.+):$/, ["Artistas que suenan como $1:", "Artistes qui sonnent comme $1 :", "Artists, die wie $1 klingen:", "Artisti che suonano come $1:", "Artistas que soam como $1:", "Artiesten die klinken als $1:"]],
    [/^See tracks by (.+)$/, ["Ver temas de $1", "Voir les titres de $1", "Tracks von $1 ansehen", "Vedi i brani di $1", "Ver faixas de $1", "Tracks van $1 bekijken"]],
    [/^The closest sounds (\d+)% like your track\.$/, ["El más cercano se parece un $1% a tu tema.", "Le plus proche ressemble à $1 % à votre titre.", "Der ähnlichste klingt zu $1 % wie dein Track.", "Il più vicino somiglia al $1% al tuo brano.", "O mais próximo soa $1% como sua faixa.", "De dichtstbijzijnde lijkt voor $1% op jouw track."]],
    [/^Most are around (\d+) BPM\.$/, ["La mayoría rondan los $1 BPM.", "La plupart sont autour de $1 BPM.", "Die meisten liegen um $1 BPM.", "La maggior parte è intorno ai $1 BPM.", "A maioria fica por volta de $1 BPM.", "De meeste zitten rond $1 BPM."]],
    [/^Most sit between (\d+) and (\d+) BPM\.$/, ["La mayoría están entre $1 y $2 BPM.", "La plupart sont entre $1 et $2 BPM.", "Die meisten liegen zwischen $1 und $2 BPM.", "La maggior parte è tra $1 e $2 BPM.", "A maioria fica entre $1 e $2 BPM.", "De meeste zitten tussen $1 en $2 BPM."]],
    [/^(\d+) of (\d+) are in a key that mixes with yours\.$/, ["$1 de $2 están en una tonalidad que mezcla con la tuya.", "$1 sur $2 sont dans une tonalité compatible avec la vôtre.", "$1 von $2 sind in einer Tonart, die zu deiner passt.", "$1 su $2 sono in una tonalità compatibile con la tua.", "$1 de $2 estão num tom que mixa com o seu.", "$1 van $2 staan in een toonsoort die met de jouwe mixt."]],
    [/^1 came out in the last 30 days\.$/, ["1 salió en los últimos 30 días.", "1 est sorti ces 30 derniers jours.", "1 ist in den letzten 30 Tagen erschienen.", "1 è uscito negli ultimi 30 giorni.", "1 saiu nos últimos 30 dias.", "1 kwam de afgelopen 30 dagen uit."]],
    [/^A label that keeps coming up: (.+)\.$/, ["Un sello que se repite: $1.", "Un label qui revient souvent : $1.", "Ein Label, das öfter auftaucht: $1.", "Un'etichetta che ricorre: $1.", "Um selo que aparece com frequência: $1.", "Een label dat vaak terugkomt: $1."]],
    [/^(\d+) came out in the last 30 days\.$/, ["$1 salieron en los últimos 30 días.", "$1 sont sortis ces 30 derniers jours.", "$1 sind in den letzten 30 Tagen erschienen.", "$1 sono usciti negli ultimi 30 giorni.", "$1 saíram nos últimos 30 dias.", "$1 kwamen de afgelopen 30 dagen uit."]],
    [/^Mostly (.+) and (.+)\.$/, ["Sobre todo $1 y $2.", "Surtout : $1 et $2.", "Vor allem $1 und $2.", "Soprattutto $1 e $2.", "Principalmente $1 e $2.", "Vooral $1 en $2."]],
    [/^Mostly (.+)\.$/, ["Sobre todo $1.", "Surtout : $1.", "Vor allem $1.", "Soprattutto $1.", "Principalmente $1.", "Vooral $1."]],
    [/^Labels that keep coming up: (.+)\.$/, ["Sellos que se repiten: $1.", "Labels qui reviennent souvent : $1.", "Labels, die öfter auftauchen: $1.", "Etichette che ricorrono: $1.", "Selos que aparecem com frequência: $1.", "Labels die vaak terugkomen: $1."]],
    // "why it matches" pieces
    [/^(\d+) BPM apart$/, ["$1 BPM de diferencia", "$1 BPM d'écart", "$1 BPM Unterschied", "$1 BPM di differenza", "$1 BPM de diferença", "$1 BPM verschil"]],
    [/^energy jump ([+−-]\d+)$/, ["salto de energía $1", "saut d'énergie $1", "Energiesprung $1", "salto di energia $1", "salto de energia $1", "energiesprong $1"]],
    [/^energy ([+−-]\d+)$/, ["energía $1", "énergie $1", "Energie $1", "energia $1", "energia $1", "energie $1"]],
    [/^(tempo around )(\d+)( BPM)$/, ["tempo de unos $2 BPM", "tempo d'environ $2 BPM", "Tempo um $2 BPM", "tempo intorno ai $2 BPM", "tempo por volta de $2 BPM", "tempo rond $2 BPM"]],
    // musical key names in tooltips
    [/^([A-G][#b]?) major$/, ["$1 mayor", "$1 majeur", "$1-Dur", "$1 maggiore", "$1 maior", "$1 majeur"]],
    [/^([A-G][#b]?) minor$/, ["$1 menor", "$1 mineur", "$1-Moll", "$1 minore", "$1 menor", "$1 mineur"]],
  ];

  // House-check explanation: "<reasons>. SimilarSounds only covers house music for now, so matches may not fit well."
  const REASONS = {
    "no steady four-on-the-floor kick": ["sin bombo four-on-the-floor constante", "pas de kick four-on-the-floor régulier", "keine durchgehende Four-on-the-Floor-Kick", "nessuna cassa four-on-the-floor costante", "sem bumbo four-on-the-floor constante", "geen vaste four-on-the-floor-kick"],
    "not tagged as dance/electronic": ["no está etiquetado como dance/electrónica", "pas classé dance/électronique", "nicht als Dance/Electronic markiert", "non etichettato come dance/elettronica", "não marcado como dance/eletrônica", "niet gelabeld als dance/elektronisch"],
    "doesn't sound like house": ["no suena a house", "ne sonne pas house", "klingt nicht nach House", "non suona house", "não soa como house", "klinkt niet als house"],
  };
  const HOUSE_TAIL = ["SimilarSounds solo cubre música house por ahora, así que las coincidencias pueden no encajar bien.", "SimilarSounds ne couvre que la house pour l'instant, les résultats peuvent donc ne pas bien coller.", "SimilarSounds deckt vorerst nur House ab, daher passen die Treffer vielleicht nicht gut.", "Per ora SimilarSounds copre solo la musica house, quindi i risultati potrebbero non essere adatti.", "Por enquanto o SimilarSounds só cobre house, então os resultados podem não combinar bem.", "SimilarSounds dekt voorlopig alleen house, dus de matches passen misschien niet goed."];

  let lang = "en";
  try { lang = localStorage.getItem("ss_lang") || "en"; } catch {}
  if (!LANGS.some(l => l[0] === lang)) lang = "en";

  const cap = s => s.charAt(0).toUpperCase() + s.slice(1);

  // Translate one plain English string (or return it unchanged)
  function tr(src) {
    if (lang === "en" || !src) return src;
    const c = COL[lang];
    const s = src.trim();
    if (!s) return src;
    const lead = src.slice(0, src.indexOf(s)), tail = src.slice(src.indexOf(s) + s.length);
    const out = trCore(s, c);
    return out == null ? src : lead + out + tail;
  }
  function trCore(s, c) {
    if (T[s]) return T[s][c];
    for (const [re, row] of P) if (re.test(s)) return s.replace(re, row[c]);
    // house-check sentence
    const hm = s.match(/^(.+)\. SimilarSounds only covers house music for now, so matches may not fit well\.$/);
    if (hm) {
      const parts = hm[1].split(", ").map((p, i) => {
        const key = p.charAt(0).toLowerCase() + p.slice(1);
        const t = REASONS[key] ? REASONS[key][c] : trCore(key, c) ?? p;
        return i === 0 ? cap(t) : t;
      });
      return parts.join(", ") + ". " + HOUSE_TAIL[c];
    }
    // "·"-separated lines (why-it-matches, filter summary, sub-genre · age)
    if (s.includes(" · ") || s.startsWith("· ")) {
      const lead = s.startsWith("· ") ? "· " : "";
      const bits = s.replace(/^· /, "").split(" · ");
      let changed = false;
      const outBits = bits.map(b => {
        const t = trPiece(b, c);
        if (t !== b) changed = true;
        return t;
      });
      return changed ? lead + outBits.join(" · ") : null;
    }
    return null;
  }
  function trPiece(b, c) {
    const lower = b.charAt(0).toLowerCase() + b.slice(1);
    // "6A→5A adjacent key" (set panel)
    const km = b.match(/^(\d+[AB]→\d+[AB]) (.+)$/);
    if (km) { const k = trCore(cap(km[2]), c); return k ? `${km[1]} ${k}` : b; }
    const t = trCore(b, c) ?? (b !== lower ? null : trCore(cap(b), c));
    return t ?? b;
  }

  // ---------- applying to the page
  const SKIP = ".t, .a, .qt, .tt, .ta, .sg-name, .sg-sub, .logo, .brand, .chip.cam, .group-n, script, style, code, kbd, [data-no-i18n]";
  const origText = new WeakMap();
  const ATTRS = ["placeholder", "aria-label", "title"];
  let applying = false;

  function translateText(node) {
    const p = node.parentElement;
    if (!p || (p.closest(SKIP) && !p.matches(".badge-new")) || p.closest("[data-i18n]") && !p.matches("[data-i18n] *")) return;
    const src = origText.has(node) ? origText.get(node) : node.textContent;
    const out = tr(src);
    if (out !== src) { origText.set(node, src); if (node.textContent !== out) node.textContent = out; }
    else if (origText.has(node)) { if (node.textContent !== src) node.textContent = src; origText.delete(node); }
  }
  function translateAttrs(el) {
    for (const a of ATTRS) {
      if (!el.hasAttribute(a)) continue;
      const key = "i18n" + a.replace(/-(\w)/g, (m, x) => x.toUpperCase());
      const src = el.dataset[key] ?? el.getAttribute(a);
      const out = tr(src);
      if (out !== src) { el.dataset[key] = src; if (el.getAttribute(a) !== out) el.setAttribute(a, out); }
      else if (el.dataset[key] != null) { el.setAttribute(a, src); delete el.dataset[key]; }
    }
  }
  function translateFragment(el) {
    if (el._i18nSrc == null) {
      el._i18nSrc = el.innerHTML;
      el._i18nKids = [...el.children].map(k => k.outerHTML);
    }
    const key = el.dataset.i18n;
    if (lang === "en" || !H[key]) { if (el.innerHTML !== el._i18nSrc) el.innerHTML = el._i18nSrc; return; }
    const html = H[key][COL[lang]].replace(/\{(\d)\}/g, (m, i) => el._i18nKids[i - 1] || "");
    if (el.innerHTML !== html) el.innerHTML = html;
  }
  function apply(root = document.body) {
    applying = true;
    try {
      const frags = root.matches?.("[data-i18n]") ? [root] : [];
      frags.push(...(root.querySelectorAll ? root.querySelectorAll("[data-i18n]") : []));
      frags.forEach(translateFragment);
      const w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
      let n; while ((n = w.nextNode())) translateText(n);
      if (root.nodeType === 1) {
        translateAttrs(root);
        root.querySelectorAll("[placeholder],[aria-label],[title]").forEach(translateAttrs);
      }
      translateTitle();
    } finally { applying = false; mo.takeRecords(); }
  }
  let titleSrc = null;
  function translateTitle() {
    const cur = document.title;
    if (titleSrc == null || (cur !== tr(titleSrc) && cur !== titleSrc)) titleSrc = cur;
    const out = tr(titleSrc);
    if (document.title !== out) document.title = out;
  }

  const mo = new MutationObserver(muts => {
    if (lang === "en") return;
    const roots = new Set();
    for (const m of muts) {
      if (m.type === "childList") m.addedNodes.forEach(n => roots.add(n));
      else if (m.type === "characterData") { origText.delete(m.target); roots.add(m.target); }
      else if (m.type === "attributes") {
        // the page set a new English value: forget the old original
        const key = "i18n" + m.attributeName.replace(/-(\w)/g, (x, c) => c.toUpperCase());
        delete m.target.dataset[key];
        roots.add(m.target);
      }
    }
    roots.forEach(n => {
      if (!n.isConnected) return;
      if (n.nodeType === 3) translateText(n);
      else if (n.nodeType === 1) apply(n);
    });
    mo.takeRecords();   // ignore the changes we just made ourselves
  });

  function setLang(code) {
    lang = LANGS.some(l => l[0] === code) ? code : "en";
    try { localStorage.setItem("ss_lang", lang); } catch {}
    document.documentElement.lang = lang === "en" ? "en" : lang;
    document.querySelectorAll("select[data-lang-select]").forEach(s => { s.value = lang; });
    apply();
    window.dispatchEvent(new CustomEvent("ss:lang", { detail: lang }));
  }

  function start() {
    document.querySelectorAll("select[data-lang-select]").forEach(sel => {
      sel.innerHTML = LANGS.map(([c, n]) => `<option value="${c}">${n}</option>`).join("");
      sel.value = lang;
      sel.addEventListener("change", () => setLang(sel.value));
    });
    document.documentElement.lang = lang === "en" ? "en" : lang;
    if (lang !== "en") apply();
    mo.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ATTRS });
    new MutationObserver(() => { if (!applying && lang !== "en") { applying = true; try { translateTitle(); } finally { applying = false; } } })
      .observe(document.querySelector("title"), { childList: true });
  }

  window.SSi18n = { tr, setLang, get lang() { return lang; }, LANGS };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
