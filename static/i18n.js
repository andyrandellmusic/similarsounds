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
    "New releases": ["Novedades", "Nouveautés", "Neuerscheinungen", "Nuove uscite", "Lançamentos", "Nieuwe releases"],
    "Or try a fresh release": ["O prueba un lanzamiento nuevo", "Ou essayez une nouveauté", "Oder probier einen neuen Release", "Oppure prova una nuova uscita", "Ou experimente um lançamento novo", "Of probeer een nieuwe release"],
    "Or try a new release": ["O prueba una novedad", "Ou essayez une nouveauté", "Oder probier eine Neuerscheinung", "Oppure prova una nuova uscita", "Ou experimente um lançamento", "Of probeer een nieuwe release"],
    "Pick a track": ["Elige un tema", "Choisissez un titre", "Track wählen", "Scegli un brano", "Escolha uma faixa", "Kies een track"],
    "Type an artist or paste a YouTube, SoundCloud or Beatport link.": ["Escribe un artista o pega un enlace de YouTube, SoundCloud o Beatport.", "Tapez un artiste ou collez un lien YouTube, SoundCloud ou Beatport.", "Gib einen Artist ein oder füge einen YouTube-, SoundCloud- oder Beatport-Link ein.", "Scrivi un artista o incolla un link di YouTube, SoundCloud o Beatport.", "Digite um artista ou cole um link do YouTube, SoundCloud ou Beatport.", "Typ een artiest of plak een YouTube-, SoundCloud- of Beatport-link."],
    "Get matches": ["Obtén coincidencias", "Obtenez des correspondances", "Treffer erhalten", "Ottieni abbinamenti", "Receba sugestões", "Krijg matches"],
    "The latest house music that fits its key, BPM, energy and sound.": ["Lo último en música house que encaja con su tonalidad, BPM, energía y sonido.", "La toute dernière house music qui colle à sa tonalité, son BPM, son énergie et son son.", "Die neueste House-Musik, die zu Tonart, BPM, Energie und Sound passt.", "L'ultima musica house in linea con tonalità, BPM, energia e suono.", "O mais novo em house music que combina com o tom, BPM, energia e som.", "De nieuwste housemuziek die past bij toonsoort, BPM, energie en sound."],
    "Build your set": ["Arma tu set", "Construisez votre set", "Stell dein Set zusammen", "Crea il tuo set", "Monte seu set", "Bouw je set"],
    "Line tracks up and see which ones mix smoothly.": ["Ordena los temas y mira cuáles mezclan bien.", "Alignez les titres et voyez lesquels s'enchaînent bien.", "Ordne Tracks an und sieh, welche gut ineinander übergehen.", "Metti in fila i brani e scopri quali si mixano bene.", "Organize as faixas e veja quais mixam bem.", "Zet tracks op volgorde en zie welke soepel mixen."],
    "Paste a track.": ["Pega un tema.", "Collez un titre.", "Füge einen Track ein.", "Incolla un brano.", "Cole uma faixa.", "Plak een track."],
    "the perfect mix": ["la mezcla perfecta", "le mix parfait", "den perfekten Mix", "il mix perfetto", "a mixagem perfeita", "de perfecte mix"],
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
    "Find what mixes next": ["Busca qué mezcla después", "Trouver le titre suivant", "Finde, was als Nächstes passt", "Trova cosa mixare dopo", "Encontre o que mixar depois", "Vind wat erna mixt"],
    "Drag to reorder": ["Arrastra para reordenar", "Glisser pour réordonner", "Zum Neuordnen ziehen", "Trascina per riordinare", "Arraste para reordenar", "Sleep om te herschikken"],
    "Move up": ["Subir", "Monter", "Nach oben", "Sposta su", "Mover para cima", "Omhoog"],
    "Move down": ["Bajar", "Descendre", "Nach unten", "Sposta giù", "Mover para baixo", "Omlaag"],
    "Remove": ["Quitar", "Retirer", "Entfernen", "Rimuovi", "Remover", "Verwijderen"],
    "Your track": ["Tu tema", "Votre titre", "Dein Track", "Il tuo brano", "Sua faixa", "Jouw track"],
    "From YouTube": ["De YouTube", "Depuis YouTube", "Von YouTube", "Da YouTube", "Do YouTube", "Van YouTube"],
    "From SoundCloud": ["De SoundCloud", "Depuis SoundCloud", "Von SoundCloud", "Da SoundCloud", "Do SoundCloud", "Van SoundCloud"],
    "From Bandcamp": ["De Bandcamp", "Depuis Bandcamp", "Von Bandcamp", "Da Bandcamp", "Do Bandcamp", "Van Bandcamp"],
    "Listen on Bandcamp": ["Escuchar en Bandcamp", "Écouter sur Bandcamp", "Auf Bandcamp anhören", "Ascolta su Bandcamp", "Ouvir no Bandcamp", "Luisteren op Bandcamp"],
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
    "TRY IT NOW": ["PRUÉBALO", "ESSAYEZ", "JETZT TESTEN", "PROVALO", "EXPERIMENTE", "PROBEER HET"],
    "NEW": ["NUEVO", "NOUVEAU", "NEU", "NUOVO", "NOVO", "NIEUW"],
    "Add to set": ["Añadir al set", "Ajouter au set", "Zum Set", "Aggiungi al set", "Adicionar ao set", "Aan set toevoegen"],
    "Find similar tracks": ["Buscar temas similares", "Titres similaires", "Ähnliche Tracks", "Trova brani simili", "Faixas parecidas", "Vergelijkbare tracks"],
    "✓ In set": ["✓ En el set", "✓ Dans le set", "✓ Im Set", "✓ Nel set", "✓ No set", "✓ In set"],
    "Find similar": ["Buscar similares", "Titres similaires", "Ähnliche finden", "Trova simili", "Buscar parecidas", "Vergelijkbare vinden"],
    "Similar": ["Similares", "Similaires", "Ähnliche", "Simili", "Parecidas", "Vergelijkbaar"],
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
    "Open": ["Abrir", "Ouvrir", "Öffnen", "Apri", "Abrir", "Openen"],
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
    "Sound": ["Sonido", "Son", "Sound", "Suono", "Som", "Sound"],
    "driving": ["contundente", "percutant", "treibend", "incalzante", "pulsante", "stuwend"],
    "laid-back": ["relajado", "posé", "entspannt", "rilassato", "relaxado", "relaxed"],
    "bright": ["brillante", "brillant", "hell", "brillante", "brilhante", "helder"],
    "dark": ["oscuro", "sombre", "dunkel", "scuro", "escuro", "donker"],
    "bass-heavy": ["con mucho bajo", "riche en basses", "bassbetont", "ricco di bassi", "grave pesado", "basrijk"],
    "airy": ["etéreo", "aérien", "luftig", "arioso", "leve", "luchtig"],
    "gritty": ["áspero", "granuleux", "rau", "graffiante", "sujo", "rauw"],
    "smooth": ["suave", "doux", "weich", "morbido", "suave", "zacht"],
    "evolving": ["cambiante", "évolutif", "wandelnd", "in evoluzione", "em evolução", "evoluerend"],
    "steady": ["constante", "régulier", "gleichmäßig", "costante", "constante", "gelijkmatig"],
    "How it sounds compared with the rest of our catalogue": ["Cómo suena comparado con el resto de nuestro catálogo", "Comment il sonne par rapport au reste de notre catalogue", "Wie er im Vergleich zum Rest unseres Katalogs klingt", "Come suona rispetto al resto del nostro catalogo", "Como soa em comparação com o resto do catálogo", "Hoe hij klinkt vergeleken met de rest van onze catalogus"],
    "Key wheel": ["Rueda de tonalidades", "Roue des tonalités", "Tonart-Rad", "Ruota delle tonalità", "Roda de tons", "Toonsoortwiel"],
    "Show all keys": ["Mostrar todas las tonalidades", "Afficher toutes les tonalités", "Alle Tonarten zeigen", "Mostra tutte le tonalità", "Mostrar todos os tons", "Alle toonsoorten tonen"],
    "Camelot key wheel": ["Rueda Camelot", "Roue Camelot", "Camelot-Rad", "Ruota Camelot", "Roda Camelot", "Camelot-wiel"],
    "Log in": ["Iniciar sesión", "Se connecter", "Anmelden", "Accedi", "Entrar", "Inloggen"],
    "Account": ["Cuenta", "Compte", "Konto", "Account", "Conta", "Account"],
    "Save your set on every device": ["Guarda tu set en todos tus dispositivos", "Gardez votre set sur tous vos appareils", "Speichere dein Set auf allen Geräten", "Salva il tuo set su tutti i dispositivi", "Salve seu set em todos os aparelhos", "Bewaar je set op al je apparaten"],
    "Keep your set and recent searches on every device.": ["Guarda tu set y tus búsquedas recientes en todos tus dispositivos.", "Retrouvez votre set et vos recherches récentes sur tous vos appareils.", "Behalte dein Set und deine letzten Suchen auf allen Geräten.", "Ritrova il tuo set e le ricerche recenti su tutti i dispositivi.", "Tenha seu set e buscas recentes em todos os aparelhos.", "Houd je set en recente zoekopdrachten op al je apparaten."],
    "Email": ["Correo electrónico", "E-mail", "E-Mail", "Email", "E-mail", "E-mail"],
    "Password": ["Contraseña", "Mot de passe", "Passwort", "Password", "Senha", "Wachtwoord"],
    "Show": ["Mostrar", "Afficher", "Zeigen", "Mostra", "Mostrar", "Tonen"],
    "Hide": ["Ocultar", "Masquer", "Verbergen", "Nascondi", "Ocultar", "Verbergen"],
    "Forgot your password?": ["¿Olvidaste tu contraseña?", "Mot de passe oublié ?", "Passwort vergessen?", "Password dimenticata?", "Esqueceu a senha?", "Wachtwoord vergeten?"],
    "New here? Create an account": ["¿Eres nuevo? Crea una cuenta", "Nouveau ? Créez un compte", "Neu hier? Konto erstellen", "Nuovo? Crea un account", "Novo por aqui? Crie uma conta", "Nieuw? Maak een account"],
    "Create an account": ["Crear una cuenta", "Créer un compte", "Konto erstellen", "Crea un account", "Criar uma conta", "Account aanmaken"],
    "Free. Just an email and a password of at least 8 characters.": ["Gratis. Solo un correo y una contraseña de al menos 8 caracteres.", "Gratuit. Juste un e-mail et un mot de passe d'au moins 8 caractères.", "Kostenlos. Nur eine E-Mail und ein Passwort mit mindestens 8 Zeichen.", "Gratis. Basta un'email e una password di almeno 8 caratteri.", "Grátis. Só um e-mail e uma senha de pelo menos 8 caracteres.", "Gratis. Alleen een e-mailadres en een wachtwoord van minstens 8 tekens."],
    "Create account": ["Crear cuenta", "Créer le compte", "Konto erstellen", "Crea account", "Criar conta", "Account aanmaken"],
    "Already have an account? Log in": ["¿Ya tienes cuenta? Inicia sesión", "Déjà un compte ? Connectez-vous", "Schon ein Konto? Anmelden", "Hai già un account? Accedi", "Já tem conta? Entrar", "Heb je al een account? Inloggen"],
    "Reset your password": ["Restablece tu contraseña", "Réinitialisez votre mot de passe", "Passwort zurücksetzen", "Reimposta la password", "Redefina sua senha", "Wachtwoord opnieuw instellen"],
    "We'll email you a link to choose a new password.": ["Te enviaremos un enlace por correo para elegir una nueva contraseña.", "Nous vous enverrons un lien par e-mail pour choisir un nouveau mot de passe.", "Wir schicken dir einen Link, um ein neues Passwort zu wählen.", "Ti invieremo un link via email per scegliere una nuova password.", "Enviaremos um link por e-mail para você escolher uma nova senha.", "We mailen je een link om een nieuw wachtwoord te kiezen."],
    "Send reset link": ["Enviar enlace", "Envoyer le lien", "Link senden", "Invia link", "Enviar link", "Link versturen"],
    "Back to log in": ["Volver a iniciar sesión", "Retour à la connexion", "Zurück zur Anmeldung", "Torna all'accesso", "Voltar para entrar", "Terug naar inloggen"],
    "Choose a new password": ["Elige una nueva contraseña", "Choisissez un nouveau mot de passe", "Wähle ein neues Passwort", "Scegli una nuova password", "Escolha uma nova senha", "Kies een nieuw wachtwoord"],
    "Save new password": ["Guardar nueva contraseña", "Enregistrer le mot de passe", "Neues Passwort speichern", "Salva nuova password", "Salvar nova senha", "Nieuw wachtwoord opslaan"],
    "Your account": ["Tu cuenta", "Votre compte", "Dein Konto", "Il tuo account", "Sua conta", "Je account"],
    "Log out": ["Cerrar sesión", "Se déconnecter", "Abmelden", "Esci", "Sair", "Uitloggen"],
    "Delete my account": ["Eliminar mi cuenta", "Supprimer mon compte", "Mein Konto löschen", "Elimina il mio account", "Excluir minha conta", "Mijn account verwijderen"],
    "Delete your account?": ["¿Eliminar tu cuenta?", "Supprimer votre compte ?", "Konto löschen?", "Eliminare l'account?", "Excluir sua conta?", "Je account verwijderen?"],
    "This permanently deletes your account and the set saved to it. Your set stays on this device.": ["Esto elimina para siempre tu cuenta y el set guardado en ella. Tu set se queda en este dispositivo.", "Cela supprime définitivement votre compte et le set qui y est enregistré. Votre set reste sur cet appareil.", "Damit werden dein Konto und das darin gespeicherte Set dauerhaft gelöscht. Dein Set bleibt auf diesem Gerät.", "Questo elimina definitivamente il tuo account e il set salvato. Il set resta su questo dispositivo.", "Isso exclui para sempre sua conta e o set salvo nela. Seu set continua neste aparelho.", "Hiermee worden je account en de opgeslagen set definitief verwijderd. Je set blijft op dit apparaat."],
    "Yes, delete my account": ["Sí, eliminar mi cuenta", "Oui, supprimer mon compte", "Ja, mein Konto löschen", "Sì, elimina il mio account", "Sim, excluir minha conta", "Ja, verwijder mijn account"],
    "Keep my account": ["Mantener mi cuenta", "Garder mon compte", "Konto behalten", "Tieni il mio account", "Manter minha conta", "Account houden"],
    "That email and password don't match.": ["Ese correo y esa contraseña no coinciden.", "Cet e-mail et ce mot de passe ne correspondent pas.", "E-Mail und Passwort passen nicht zusammen.", "Email e password non corrispondono.", "Esse e-mail e essa senha não correspondem.", "Dat e-mailadres en wachtwoord horen niet bij elkaar."],
    "Please confirm your email first - check your inbox for the link.": ["Confirma primero tu correo: busca el enlace en tu bandeja de entrada.", "Confirmez d'abord votre e-mail : le lien est dans votre boîte de réception.", "Bitte bestätige zuerst deine E-Mail – der Link ist in deinem Posteingang.", "Conferma prima la tua email: trovi il link nella posta in arrivo.", "Confirme seu e-mail primeiro: o link está na sua caixa de entrada.", "Bevestig eerst je e-mailadres – de link staat in je inbox."],
    "There's already an account with that email. Try logging in.": ["Ya hay una cuenta con ese correo. Prueba a iniciar sesión.", "Un compte existe déjà avec cet e-mail. Essayez de vous connecter.", "Mit dieser E-Mail gibt es schon ein Konto. Versuch dich anzumelden.", "Esiste già un account con questa email. Prova ad accedere.", "Já existe uma conta com esse e-mail. Tente entrar.", "Er is al een account met dit e-mailadres. Probeer in te loggen."],
    "Please use a password of at least 8 characters.": ["Usa una contraseña de al menos 8 caracteres.", "Utilisez un mot de passe d'au moins 8 caractères.", "Bitte nutze ein Passwort mit mindestens 8 Zeichen.", "Usa una password di almeno 8 caratteri.", "Use uma senha de pelo menos 8 caracteres.", "Gebruik een wachtwoord van minstens 8 tekens."],
    "Too many attempts - please wait a few minutes and try again.": ["Demasiados intentos: espera unos minutos y vuelve a probar.", "Trop de tentatives : patientez quelques minutes et réessayez.", "Zu viele Versuche – bitte warte ein paar Minuten.", "Troppi tentativi: attendi qualche minuto e riprova.", "Muitas tentativas: aguarde alguns minutos e tente de novo.", "Te veel pogingen – wacht een paar minuten en probeer het opnieuw."],
    "Please enter a valid email address.": ["Introduce un correo válido.", "Saisissez une adresse e-mail valide.", "Bitte gib eine gültige E-Mail-Adresse ein.", "Inserisci un indirizzo email valido.", "Digite um e-mail válido.", "Vul een geldig e-mailadres in."],
    "Can't reach the login service right now. Check your connection.": ["No se puede conectar con el servicio de acceso. Revisa tu conexión.", "Impossible de joindre le service de connexion. Vérifiez votre connexion.", "Der Anmeldedienst ist gerade nicht erreichbar. Prüf deine Verbindung.", "Impossibile raggiungere il servizio di accesso. Controlla la connessione.", "Não foi possível acessar o serviço de login. Verifique sua conexão.", "De inlogdienst is nu niet bereikbaar. Controleer je verbinding."],
    "Something went wrong. Please try again.": ["Algo ha fallado. Inténtalo de nuevo.", "Un problème est survenu. Réessayez.", "Etwas ist schiefgelaufen. Bitte versuch es erneut.", "Qualcosa è andato storto. Riprova.", "Algo deu errado. Tente de novo.", "Er ging iets mis. Probeer het opnieuw."],
    "Logged in - your set is saved to your account": ["Sesión iniciada: tu set se guarda en tu cuenta", "Connecté : votre set est enregistré dans votre compte", "Angemeldet – dein Set wird in deinem Konto gespeichert", "Accesso eseguito: il set è salvato nel tuo account", "Você entrou: seu set fica salvo na sua conta", "Ingelogd – je set wordt in je account bewaard"],
    "Account created - you're logged in": ["Cuenta creada: ya has iniciado sesión", "Compte créé : vous êtes connecté", "Konto erstellt – du bist angemeldet", "Account creato: hai effettuato l'accesso", "Conta criada: você já entrou", "Account aangemaakt – je bent ingelogd"],
    "Nearly done! We've sent you an email - click the link in it to confirm your account.": ["¡Casi listo! Te hemos enviado un correo: pulsa el enlace para confirmar tu cuenta.", "Presque fini ! Nous vous avons envoyé un e-mail : cliquez sur le lien pour confirmer votre compte.", "Fast geschafft! Wir haben dir eine E-Mail geschickt – klick auf den Link, um dein Konto zu bestätigen.", "Quasi fatto! Ti abbiamo inviato un'email: clicca il link per confermare l'account.", "Quase lá! Enviamos um e-mail: clique no link para confirmar sua conta.", "Bijna klaar! We hebben je een e-mail gestuurd – klik op de link om je account te bevestigen."],
    "If there's an account for that email, we've sent a link to reset your password.": ["Si hay una cuenta con ese correo, te hemos enviado un enlace para restablecer la contraseña.", "S'il existe un compte pour cet e-mail, nous avons envoyé un lien de réinitialisation.", "Falls es ein Konto mit dieser E-Mail gibt, haben wir einen Link zum Zurücksetzen geschickt.", "Se esiste un account con questa email, ti abbiamo inviato un link per reimpostare la password.", "Se houver uma conta com esse e-mail, enviamos um link para redefinir a senha.", "Als er een account bij dit e-mailadres hoort, hebben we een resetlink gestuurd."],
    "Password changed - you're logged in": ["Contraseña cambiada: ya has iniciado sesión", "Mot de passe modifié : vous êtes connecté", "Passwort geändert – du bist angemeldet", "Password cambiata: hai effettuato l'accesso", "Senha alterada: você já entrou", "Wachtwoord gewijzigd – je bent ingelogd"],
    "Logged out. Your set stays on this device.": ["Sesión cerrada. Tu set se queda en este dispositivo.", "Déconnecté. Votre set reste sur cet appareil.", "Abgemeldet. Dein Set bleibt auf diesem Gerät.", "Disconnesso. Il set resta su questo dispositivo.", "Você saiu. Seu set continua neste aparelho.", "Uitgelogd. Je set blijft op dit apparaat."],
    "Couldn't delete your account. Please try again, or email us.": ["No se pudo eliminar tu cuenta. Inténtalo de nuevo o escríbenos.", "Impossible de supprimer votre compte. Réessayez ou écrivez-nous.", "Konto konnte nicht gelöscht werden. Versuch es erneut oder schreib uns.", "Impossibile eliminare l'account. Riprova o scrivici.", "Não foi possível excluir sua conta. Tente de novo ou envie um e-mail.", "Je account kon niet worden verwijderd. Probeer opnieuw of mail ons."],
    "Your account and saved data have been deleted": ["Tu cuenta y tus datos guardados se han eliminado", "Votre compte et vos données ont été supprimés", "Dein Konto und deine gespeicherten Daten wurden gelöscht", "Account e dati salvati eliminati", "Sua conta e seus dados foram excluídos", "Je account en opgeslagen gegevens zijn verwijderd"],
    "Email confirmed - you're logged in": ["Correo confirmado: ya has iniciado sesión", "E-mail confirmé : vous êtes connecté", "E-Mail bestätigt – du bist angemeldet", "Email confermata: hai effettuato l'accesso", "E-mail confirmado: você já entrou", "E-mailadres bevestigd – je bent ingelogd"],
    "Log in / Sign up": ["Iniciar sesión / Registrarse", "Connexion / Inscription", "Anmelden / Registrieren", "Accedi / Registrati", "Entrar / Cadastrar", "Inloggen / Aanmelden"],
    "Signed in": ["Sesión iniciada", "Connecté", "Angemeldet", "Connesso", "Conectado", "Ingelogd"],
    "Name": ["Nombre", "Nom", "Name", "Nome", "Nome", "Naam"],
    "Your name": ["Tu nombre", "Votre nom", "Dein Name", "Il tuo nome", "Seu nome", "Je naam"],
    "Save name": ["Guardar nombre", "Enregistrer le nom", "Name speichern", "Salva nome", "Salvar nome", "Naam opslaan"],
    "Name saved": ["Nombre guardado", "Nom enregistré", "Name gespeichert", "Nome salvato", "Nome salvo", "Naam opgeslagen"],
    "Log in or sign up": ["Inicia sesión o regístrate", "Connectez-vous ou inscrivez-vous", "Anmelden oder registrieren", "Accedi o registrati", "Entre ou cadastre-se", "Inloggen of aanmelden"],
    "Free. Just your name, email and a password of at least 8 characters.": ["Gratis. Solo tu nombre, tu correo y una contraseña de al menos 8 caracteres.", "Gratuit. Juste votre nom, votre e-mail et un mot de passe d'au moins 8 caractères.", "Kostenlos. Nur dein Name, deine E-Mail und ein Passwort mit mindestens 8 Zeichen.", "Gratis. Bastano nome, email e una password di almeno 8 caratteri.", "Grátis. Só seu nome, e-mail e uma senha de pelo menos 8 caracteres.", "Gratis. Alleen je naam, e-mailadres en een wachtwoord van minstens 8 tekens."],
    "Signed in - your set is saved to your account": ["Sesión iniciada: tu set se guarda en tu cuenta", "Connecté : votre set est enregistré dans votre compte", "Angemeldet – dein Set wird in deinem Konto gespeichert", "Accesso eseguito: il set è salvato nel tuo account", "Você entrou: seu set fica salvo na sua conta", "Ingelogd – je set wordt in je account bewaard"],
    "match": ["parecido", "ressemblance", "ähnlich", "simile", "parecido", "match"],
    "Try our new feature now": ["Prueba nuestra nueva función", "Essayez notre nouvelle fonction", "Probier unsere neue Funktion aus", "Prova la nostra nuova funzione", "Experimente nosso novo recurso", "Probeer onze nieuwe functie"],
    "Set builder": ["Creador de sets", "Créateur de set", "Set-Builder", "Crea set", "Montador de sets", "Setbouwer"],
    "Try for free now": ["Pruébalo gratis ya", "Essayez gratuitement", "Jetzt kostenlos testen", "Provalo gratis ora", "Experimente grátis agora", "Probeer nu gratis"],
    "1 free search left": ["Te queda 1 búsqueda gratis", "Il vous reste 1 recherche gratuite", "Noch 1 kostenlose Suche", "Ti resta 1 ricerca gratuita", "Resta 1 busca grátis", "Nog 1 gratis zoekopdracht"],
    "Unlimited searches": ["Búsquedas ilimitadas", "Recherches illimitées", "Unbegrenzte Suchen", "Ricerche illimitate", "Buscas ilimitadas", "Onbeperkt zoeken"],
    "No free searches left.": ["No te quedan búsquedas gratis.", "Plus de recherches gratuites.", "Keine kostenlosen Suchen mehr.", "Ricerche gratuite esaurite.", "Sem buscas grátis.", "Geen gratis zoekopdrachten meer."],
    "Create a free account for 2 more": ["Crea una cuenta gratis para 2 más", "Créez un compte gratuit pour 2 de plus", "Kostenloses Konto für 2 weitere", "Crea un account gratis per altre 2", "Crie uma conta grátis para mais 2", "Maak een gratis account voor nog 2"],
    "You've used your 3 free searches": ["Has usado tus 3 búsquedas gratis", "Vous avez utilisé vos 3 recherches gratuites", "Du hast deine 3 kostenlosen Suchen genutzt", "Hai usato le tue 3 ricerche gratuite", "Você usou suas 3 buscas grátis", "Je hebt je 3 gratis zoekopdrachten gebruikt"],
    "Create a free account to get 2 more searches. It only takes a minute.": ["Crea una cuenta gratis y consigue 2 búsquedas más. Solo lleva un minuto.", "Créez un compte gratuit pour obtenir 2 recherches de plus. Ça ne prend qu'une minute.", "Erstell ein kostenloses Konto und erhalte 2 weitere Suchen. Dauert nur eine Minute.", "Crea un account gratuito per avere altre 2 ricerche. Ci vuole un minuto.", "Crie uma conta grátis e ganhe mais 2 buscas. Leva só um minuto.", "Maak een gratis account en krijg nog 2 zoekopdrachten. Het duurt maar een minuut."],
    "Create a free account to get 2 more searches.": ["Crea una cuenta gratis y consigue 2 búsquedas más.", "Créez un compte gratuit pour obtenir 2 recherches de plus.", "Erstell ein kostenloses Konto und erhalte 2 weitere Suchen.", "Crea un account gratuito per avere altre 2 ricerche.", "Crie uma conta grátis e ganhe mais 2 buscas.", "Maak een gratis account en krijg nog 2 zoekopdrachten."],
    "Create a free account": ["Crear una cuenta gratis", "Créer un compte gratuit", "Kostenloses Konto erstellen", "Crea un account gratuito", "Criar uma conta grátis", "Gratis account maken"],
    "Your free searches have run out": ["Se han acabado tus búsquedas gratis", "Vos recherches gratuites sont épuisées", "Deine kostenlosen Suchen sind aufgebraucht", "Le ricerche gratuite sono finite", "Suas buscas grátis acabaram", "Je gratis zoekopdrachten zijn op"],
    "Unlimited searches and \"Similar\" finds": ["Búsquedas y \"Similares\" ilimitados", "Recherches et « Similaires » illimitées", "Unbegrenzte Suchen und „Ähnliche“", "Ricerche e \"Simili\" illimitate", "Buscas e \"Parecidas\" ilimitadas", "Onbeperkt zoeken en \"Vergelijkbaar\""],
    "Build and share as many sets as you like": ["Crea y comparte todos los sets que quieras", "Créez et partagez autant de sets que vous voulez", "Stell so viele Sets zusammen und teile sie, wie du willst", "Crea e condividi tutti i set che vuoi", "Monte e compartilhe quantos sets quiser", "Bouw en deel zoveel sets als je wilt"],
    "Cancel anytime": ["Cancela cuando quieras", "Résiliable à tout moment", "Jederzeit kündbar", "Disdici quando vuoi", "Cancele quando quiser", "Altijd opzegbaar"],
    "/month": ["/mes", "/mois", "/Monat", "/mese", "/mês", "/maand"],
    "Subscriptions coming soon": ["Suscripciones muy pronto", "Abonnements bientôt disponibles", "Abos bald verfügbar", "Abbonamenti in arrivo", "Assinaturas em breve", "Abonnementen binnenkort"],
    "We're putting the finishing touches on subscriptions. Your saved set is safe in your account in the meantime.": ["Estamos ultimando las suscripciones. Mientras tanto, tu set guardado está a salvo en tu cuenta.", "Nous finalisons les abonnements. En attendant, votre set est en sécurité dans votre compte.", "Wir legen gerade letzte Hand an die Abos. Dein gespeichertes Set ist so lange sicher in deinem Konto.", "Stiamo ultimando gli abbonamenti. Nel frattempo il tuo set è al sicuro nel tuo account.", "Estamos finalizando as assinaturas. Enquanto isso, seu set salvo está seguro na sua conta.", "We leggen de laatste hand aan abonnementen. Je opgeslagen set staat zolang veilig in je account."],
    "Unlimited searches are coming soon with SimilarSounds Unlimited: £4.99 a month, cancel anytime.": ["Muy pronto, búsquedas ilimitadas con SimilarSounds Unlimited: 4,99 £ al mes, cancela cuando quieras.", "Bientôt, des recherches illimitées avec SimilarSounds Unlimited : 4,99 £ par mois, résiliable à tout moment.", "Bald unbegrenzte Suchen mit SimilarSounds Unlimited: 4,99 £ im Monat, jederzeit kündbar.", "Presto ricerche illimitate con SimilarSounds Unlimited: 4,99 £ al mese, disdici quando vuoi.", "Em breve, buscas ilimitadas com o SimilarSounds Unlimited: £4,99 por mês, cancele quando quiser.", "Binnenkort onbeperkt zoeken met SimilarSounds Unlimited: £4,99 per maand, altijd opzegbaar."],
    "free searches": ["búsquedas gratis", "recherches gratuites", "kostenlose Suchen", "ricerche gratuite", "buscas grátis", "gratis zoekopdrachten"],
    "used": ["usadas", "utilisées", "genutzt", "usate", "usadas", "gebruikt"],
    "free search": ["búsqueda gratis", "recherche gratuite", "kostenlose Suche", "ricerca gratuita", "busca grátis", "gratis zoekopdracht"],
    "Unlimited": ["Ilimitado", "Illimité", "Unbegrenzt", "Illimitato", "Ilimitado", "Onbeperkt"],
    "Energy": ["Energía", "Énergie", "Energie", "Energia", "Energia", "Energie"],
    "You have 1 credit left": ["Te queda 1 crédito", "Il vous reste 1 crédit", "Du hast noch 1 Credit", "Ti resta 1 credito", "Você tem 1 crédito restante", "Je hebt nog 1 credit"],
    "When it's used, you'll get 2 more free searches 24 hours later.": ["Cuando lo uses, tendrás 2 búsquedas gratis más 24 horas después.", "Une fois utilisé, vous aurez 2 recherches gratuites de plus 24 heures plus tard.", "Wenn du ihn genutzt hast, bekommst du 24 Stunden später 2 weitere kostenlose Suchen.", "Quando lo usi, avrai altre 2 ricerche gratuite 24 ore dopo.", "Quando usá-lo, você terá mais 2 buscas grátis 24 horas depois.", "Als je hem gebruikt, krijg je 24 uur later 2 extra gratis zoekopdrachten."],
    "Not now": ["Ahora no", "Pas maintenant", "Nicht jetzt", "Non ora", "Agora não", "Niet nu"],
    "Got it": ["Entendido", "Compris", "Verstanden", "Ho capito", "Entendi", "Begrepen"],
    "Continue as": ["Continuar como", "Continuer en tant que", "Weiter als", "Continua come", "Continuar como", "Doorgaan als"],
    "Use a different account": ["Usar otra cuenta", "Utiliser un autre compte", "Anderes Konto verwenden", "Usa un altro account", "Usar outra conta", "Een ander account gebruiken"],
    "Sign in with Face ID": ["Iniciar sesión con Face ID", "Se connecter avec Face ID", "Mit Face ID anmelden", "Accedi con Face ID", "Entrar com Face ID", "Inloggen met Face ID"],
    "Sign in with Face ID next time?": ["¿Iniciar sesión con Face ID la próxima vez?", "Se connecter avec Face ID la prochaine fois ?", "Nächstes Mal mit Face ID anmelden?", "Accedere con Face ID la prossima volta?", "Entrar com Face ID da próxima vez?", "Volgende keer inloggen met Face ID?"],
    "Turn on Face ID sign-in": ["Activar inicio con Face ID", "Activer la connexion Face ID", "Face-ID-Anmeldung aktivieren", "Attiva l'accesso con Face ID", "Ativar entrada com Face ID", "Inloggen met Face ID aanzetten"],
    "No thanks": ["No, gracias", "Non merci", "Nein danke", "No grazie", "Não, obrigado", "Nee, bedankt"],
    "Use my password instead": ["Usar mi contraseña", "Utiliser mon mot de passe", "Stattdessen mein Passwort verwenden", "Usa la mia password", "Usar minha senha", "Mijn wachtwoord gebruiken"],
    "Face ID sign-in": ["Inicio con Face ID", "Connexion Face ID", "Face-ID-Anmeldung", "Accesso con Face ID", "Entrada com Face ID", "Inloggen met Face ID"],
    "Turn on": ["Activar", "Activer", "Aktivieren", "Attiva", "Ativar", "Aanzetten"],
    "Turn off": ["Desactivar", "Désactiver", "Deaktivieren", "Disattiva", "Desativar", "Uitzetten"],
    "Sign in as": ["Entrar como", "Se connecter en tant que", "Anmelden als", "Accedi come", "Entrar como", "Inloggen als"],
    "Scroll down": ["Desplázate", "Faites défiler", "Nach unten scrollen", "Scorri giù", "Role para baixo", "Scroll omlaag"],
    "Please log in again": ["Vuelve a iniciar sesión", "Veuillez vous reconnecter", "Bitte melde dich erneut an", "Accedi di nuovo", "Entre novamente", "Log opnieuw in"],
    "Intro track": ["Tema de intro", "Morceau d'intro", "Intro-Track", "Traccia d'apertura", "Faixa de abertura", "Intro-track"],
    "End track": ["Tema final", "Morceau de fin", "Schluss-Track", "Traccia finale", "Faixa final", "Slottrack"],
    "Warm-up": ["Calentamiento", "Échauffement", "Warm-up", "Riscaldamento", "Aquecimento", "Warming-up"],
    "Build": ["Subida", "Montée", "Aufbau", "Crescendo", "Construção", "Opbouw"],
    "Peak track": ["Tema cumbre", "Morceau phare", "Peak-Track", "Traccia di picco", "Faixa de pico", "Piektrack"],
    "Peak time": ["Hora punta", "Moment fort", "Peak-Time", "Momento clou", "Horário de pico", "Piekmoment"],
    "Cool down": ["Bajada", "Redescente", "Ausklang", "Defaticamento", "Desaceleração", "Afkoelen"],
    "Are you sure you want to delete set?": ["¿Seguro que quieres borrar el set?", "Voulez-vous vraiment supprimer le set ?", "Möchtest du das Set wirklich löschen?", "Vuoi davvero eliminare il set?", "Tem certeza de que quer apagar o set?", "Weet je zeker dat je de set wilt verwijderen?"],
    "Yes": ["Sí", "Oui", "Ja", "Sì", "Sim", "Ja"],
    "No": ["No", "Non", "Nein", "No", "Não", "Nee"],
    "Artist, track or link…": ["Artista, tema o enlace…", "Artiste, titre ou lien…", "Künstler, Track oder Link…", "Artista, brano o link…", "Artista, faixa ou link…", "Artiest, track of link…"],
    "More": ["Más", "Plus", "Mehr", "Altro", "Mais", "Meer"],
    "Include older releases": ["Incluir lanzamientos antiguos", "Inclure les sorties plus anciennes", "Ältere Releases einbeziehen", "Includi uscite più vecchie", "Incluir lançamentos antigos", "Oudere releases meenemen"],
    "Widen BPM to ±10": ["Ampliar BPM a ±10", "Élargir le BPM à ±10", "BPM auf ±10 erweitern", "Allarga BPM a ±10", "Ampliar BPM para ±10", "BPM verruimen naar ±10"],
    "Any sub-genre": ["Cualquier subgénero", "Tous sous-genres", "Jedes Subgenre", "Qualsiasi sottogenere", "Qualquer subgênero", "Elk subgenre"],
    "Include all keys": ["Incluir todas las tonalidades", "Inclure toutes les tonalités", "Alle Tonarten einbeziehen", "Includi tutte le tonalità", "Incluir todos os tons", "Alle toonsoorten meenemen"],
    "No matches with these filters. Try widening them:": ["No hay coincidencias con estos filtros. Prueba a ampliarlos:", "Aucune correspondance avec ces filtres. Essayez de les élargir :", "Keine Treffer mit diesen Filtern. Erweitere sie:", "Nessun risultato con questi filtri. Prova ad allargarli:", "Nenhuma correspondência com esses filtros. Tente ampliá-los:", "Geen matches met deze filters. Probeer ze te verruimen:"],
    "No matches found for this track yet. New releases arrive every day, so try again soon.": ["Aún no hay coincidencias para este tema. Llegan lanzamientos nuevos cada día: vuelve a probar pronto.", "Pas encore de correspondances pour ce titre. De nouvelles sorties arrivent chaque jour : réessayez bientôt.", "Noch keine Treffer für diesen Track. Jeden Tag kommen neue Releases – versuch es bald wieder.", "Ancora nessun risultato per questo brano. Ogni giorno arrivano nuove uscite: riprova presto.", "Ainda não há correspondências para esta faixa. Chegam lançamentos novos todos os dias: tente de novo em breve.", "Nog geen matches voor deze track. Er komen elke dag nieuwe releases bij, probeer het snel opnieuw."],
    "Continue with Google": ["Continuar con Google", "Continuer avec Google", "Weiter mit Google", "Continua con Google", "Continuar com o Google", "Doorgaan met Google"],
    "or": ["o", "ou", "oder", "o", "ou", "of"],
    "Import tracklist": ["Importar tracklist", "Importer une tracklist", "Tracklist importieren", "Importa tracklist", "Importar tracklist", "Tracklist importeren"],
    "Or import a tracklist": ["O importa una tracklist", "Ou importez une tracklist", "Oder Tracklist importieren", "Oppure importa una tracklist", "Ou importe uma tracklist", "Of importeer een tracklist"],
    "Import a tracklist": ["Importar una tracklist", "Importer une tracklist", "Tracklist importieren", "Importa una tracklist", "Importar uma tracklist", "Een tracklist importeren"],
    "Import": ["Importar", "Importer", "Importieren", "Importa", "Importar", "Importeren"],
    "Type the artist and title of each track in order. Got a whole tracklist? Paste it into the first box and we'll split it up for you.": [
      "Escribe el artista y el título de cada tema en orden. ¿Tienes una tracklist entera? Pégala en la primera casilla y la separamos por ti.",
      "Tape l'artiste et le titre de chaque morceau dans l'ordre. Tu as une tracklist complète ? Colle-la dans la première case et on la découpe pour toi.",
      "Gib Künstler und Titel jedes Tracks der Reihe nach ein. Ganze Tracklist? Füge sie ins erste Feld ein, wir teilen sie für dich auf.",
      "Scrivi artista e titolo di ogni brano in ordine. Hai una tracklist intera? Incollala nella prima casella e la dividiamo noi.",
      "Digite o artista e o título de cada faixa em ordem. Tem uma tracklist inteira? Cole na primeira caixa e nós separamos para você.",
      "Typ de artiest en titel van elk nummer op volgorde. Hele tracklist? Plak hem in het eerste vak en wij splitsen hem voor je."],
    "Title": ["Título", "Titre", "Titel", "Titolo", "Título", "Titel"],
    "+ Add another track": ["+ Añadir otro tema", "+ Ajouter un morceau", "+ Weiteren Track hinzufügen", "+ Aggiungi un altro brano", "+ Adicionar outra faixa", "+ Nog een nummer toevoegen"],
    "Remove this track": ["Quitar este tema", "Retirer ce morceau", "Diesen Track entfernen", "Rimuovi questo brano", "Remover esta faixa", "Dit nummer verwijderen"],
    "Add at least one track first.": ["Añade al menos un tema primero.", "Ajoute d'abord au moins un morceau.", "Füge zuerst mindestens einen Track hinzu.", "Aggiungi prima almeno un brano.", "Adicione pelo menos uma faixa primeiro.", "Voeg eerst minstens één nummer toe."],
    "Sort by": ["Ordenar por", "Trier par", "Sortieren nach", "Ordina per", "Ordenar por", "Sorteren op"],
    "Hear the mix": ["Escucha la mezcla", "Écoute le mix", "Mix anhören", "Ascolta il mix", "Ouça a mixagem", "Hoor de mix"],
    "Hear it": ["Escúchala", "Écouter", "Anhören", "Ascolta", "Ouvir", "Luister"],
    "Getting the mix ready…": ["Preparando la mezcla…", "Préparation du mix…", "Mix wird vorbereitet…", "Preparo il mix…", "Preparando a mixagem…", "Mix wordt klaargezet…"],
    "Stop the mix": ["Parar la mezcla", "Arrêter le mix", "Mix stoppen", "Ferma il mix", "Parar a mixagem", "Mix stoppen"],
    "Couldn't load that mix. Try another track.": ["No se pudo cargar esa mezcla. Prueba otro tema.", "Impossible de charger ce mix. Essaie un autre morceau.", "Dieser Mix konnte nicht geladen werden. Versuch einen anderen Track.", "Impossibile caricare il mix. Prova un altro brano.", "Não foi possível carregar a mixagem. Tente outra faixa.", "Die mix kon niet laden. Probeer een ander nummer."],
    "Or describe a sound": ["O describe un sonido", "Ou décris un son", "Oder beschreib einen Sound", "Oppure descrivi un suono", "Ou descreva um som", "Of beschrijf een geluid"],
    "Describe a sound… e.g. warm sunset deep house with saxophone": ["Describe un sonido… p. ej. deep house cálido al atardecer con saxo", "Décris un son… ex. deep house chaude au coucher du soleil avec saxo", "Beschreib einen Sound… z. B. warmer Sunset-Deep-House mit Saxophon", "Descrivi un suono… es. deep house caldo al tramonto con sax", "Descreva um som… ex. deep house quente ao pôr do sol com sax", "Beschrijf een geluid… bv. warme sunset deep house met saxofoon"],
    "Describe a sound": ["Describe un sonido", "Décris un son", "Beschreib einen Sound", "Descrivi un suono", "Descreva um som", "Beschrijf een geluid"],
    "Listening for that sound…": ["Buscando ese sonido…", "On cherche ce son…", "Wir suchen diesen Sound…", "Cerco quel suono…", "Procurando esse som…", "We zoeken dat geluid…"],
    "We didn't catch that sound": ["No reconocimos ese sonido", "On n'a pas reconnu ce son", "Diesen Sound haben wir nicht erkannt", "Non abbiamo riconosciuto quel suono", "Não reconhecemos esse som", "Dat geluid herkenden we niet"],
    "Try describing instruments, vocals, a mood or a time of day. For example:": ["Prueba a describir instrumentos, voces, un estado de ánimo o un momento del día. Por ejemplo:", "Décris des instruments, des voix, une ambiance ou un moment de la journée. Par exemple :", "Beschreib Instrumente, Vocals, eine Stimmung oder eine Tageszeit. Zum Beispiel:", "Descrivi strumenti, voci, un mood o un momento della giornata. Per esempio:", "Descreva instrumentos, vozes, um clima ou uma hora do dia. Por exemplo:", "Beschrijf instrumenten, vocals, een sfeer of een moment van de dag. Bijvoorbeeld:"],
    "Plan a whole set in seconds": ["Planifica una sesión entera en segundos", "Planifiez un set entier en quelques secondes", "Ein ganzes Set in Sekunden planen", "Pianifica un set intero in pochi secondi", "Planeje um set inteiro em segundos", "Plan een hele set in seconden"],
    "Plan my gig": ["Planifica mi sesión", "Planifier mon set", "Meinen Gig planen", "Pianifica il mio set", "Planejar meu set", "Plan mijn set"],
    "Plan a whole gig": ["Planifica una sesión entera", "Planifier tout un set", "Ganzen Gig planen", "Pianifica un set intero", "Planejar um set inteiro", "Plan een hele set"],
    "Or plan a whole gig": ["O planifica una sesión entera", "Ou planifie tout un set", "Oder plane einen ganzen Gig", "Oppure pianifica un set intero", "Ou planeje um set inteiro", "Of plan een hele set"],
    "A whole set for your time slot": ["Una sesión entera para tu franja", "Un set complet pour ton créneau", "Ein ganzes Set für deinen Slot", "Un set intero per il tuo slot", "Um set inteiro para o seu horário", "Een hele set voor je tijdslot"],
    "Tell us how long you're playing and when. We'll build the whole set from the newest releases, every track mixing into the next.": ["Dinos cuánto tiempo tocas y cuándo. Construimos la sesión entera con los últimos lanzamientos, cada tema mezclando con el siguiente.", "Dis-nous combien de temps tu joues et quand. On construit tout le set avec les dernières sorties, chaque morceau se mixant avec le suivant.", "Sag uns, wie lange und wann du spielst. Wir bauen das ganze Set aus den neuesten Releases, jeder Track mixt in den nächsten.", "Dicci quanto suoni e quando. Costruiamo tutto il set con le ultime uscite, ogni brano si mixa col successivo.", "Diga quanto tempo e quando você toca. Montamos o set inteiro com os lançamentos mais novos, cada faixa mixando na próxima.", "Vertel hoe lang en wanneer je draait. Wij bouwen de hele set met de nieuwste releases, elk nummer mixt in het volgende."],
    "How long": ["Duración", "Durée", "Dauer", "Durata", "Duração", "Hoe lang"],
    "Your slot": ["Tu franja", "Ton créneau", "Dein Slot", "Il tuo slot", "Seu horário", "Je tijdslot"],
    "Vibe": ["Estilo", "Ambiance", "Vibe", "Vibe", "Vibe", "Vibe"],
    "Any house": ["Cualquier house", "Toute la house", "Jeder House", "Qualsiasi house", "Qualquer house", "Alle house"],
    "1 hour": ["1 hora", "1 heure", "1 Stunde", "1 ora", "1 hora", "1 uur"], "1½ hours": ["1½ horas", "1h30", "1½ Stunden", "1 ora e mezza", "1h30", "1½ uur"],
    "2 hours": ["2 horas", "2 heures", "2 Stunden", "2 ore", "2 horas", "2 uur"], "3 hours": ["3 horas", "3 heures", "3 Stunden", "3 ore", "3 horas", "3 uur"],
    "Closing": ["Cierre", "Closing", "Closing", "Chiusura", "Encerramento", "Afsluiter"], "All night": ["Toda la noche", "Toute la nuit", "Die ganze Nacht", "Tutta la notte", "A noite toda", "De hele nacht"],
    "Plan my set": ["Planificar mi sesión", "Planifier mon set", "Set planen", "Pianifica il set", "Planejar meu set", "Plan mijn set"],
    "Building your set…": ["Construyendo tu sesión…", "Construction de ton set…", "Dein Set wird gebaut…", "Costruisco il tuo set…", "Montando seu set…", "Je set wordt gebouwd…"],
    "Fresh for your set": ["Novedades para tu sesión", "Nouveautés pour ton set", "Neu für dein Set", "Novità per il tuo set", "Novidades para o seu set", "Vers voor je set"],
    "Goes with": ["Va con", "Va avec", "Passt zu", "Va con", "Combina com", "Past bij"],
    "Search a track": ["Busca un tema", "Chercher un titre", "Track suchen", "Cerca un brano", "Buscar uma faixa", "Zoek een nummer"],
    "Search by": ["Buscar por", "Chercher par", "Suchen nach", "Cerca per", "Buscar por", "Zoeken op"],
    "Try": ["Prueba", "Essaie", "Probier", "Prova", "Experimente", "Probeer"],
    "Plan a gig": ["Planifica una sesión", "Planifier un set", "Gig planen", "Pianifica un set", "Planejar um set", "Plan een set"],
    "Add to my set": ["Añadir a mi set", "Ajouter à mon set", "Zu meinem Set hinzufügen", "Aggiungi al mio set", "Adicionar ao meu set", "Aan mijn set toevoegen"],
    "Replace my set": ["Reemplazar mi set", "Remplacer mon set", "Mein Set ersetzen", "Sostituisci il mio set", "Substituir meu set", "Mijn set vervangen"],
    "Watch how it works · 45s": ["Mira cómo funciona · 45 s", "Voir comment ça marche · 45 s", "So funktioniert es · 45 Sek.", "Guarda come funziona · 45 s", "Veja como funciona · 45 s", "Bekijk hoe het werkt · 45 s"],
    "Search less.": ["Busca menos.", "Cherchez moins.", "Weniger suchen.", "Cerca di meno.", "Procure menos.", "Minder zoeken."],
    "Play more.": ["Pincha más.", "Mixez plus.", "Mehr auflegen.", "Suona di più.", "Toque mais.", "Meer draaien."],
    "Fix this gap": ["Arreglar hueco", "Combler le trou", "Lücke füllen", "Sistema il passaggio", "Corrigir lacuna", "Gat dichten"],
    "Find a track to put in between": ["Busca un tema para poner en medio", "Trouver un titre à placer entre les deux", "Einen Track dazwischen finden", "Trova un brano da mettere in mezzo", "Achar uma faixa para pôr no meio", "Zoek een track voor ertussen"],
    "Fix this gap: find a track to put in between": ["Arregla este hueco: busca un tema para poner en medio", "Combler ce trou : trouver un titre à placer entre les deux", "Lücke füllen: einen Track dazwischen finden", "Sistema questo passaggio: trova un brano da mettere in mezzo", "Corrigir esta lacuna: achar uma faixa para pôr no meio", "Gat dichten: zoek een track voor ertussen"],
    "These mix well with both tracks:": ["Estos mezclan bien con ambos temas:", "Ceux-ci se mixent bien avec les deux :", "Diese passen gut zu beiden Tracks:", "Questi si mixano bene con entrambi:", "Estas mixam bem com as duas faixas:", "Deze mixen goed met beide tracks:"],
    "These work with both tracks:": ["Estos funcionan con ambos temas:", "Ceux-ci fonctionnent avec les deux :", "Diese funktionieren mit beiden Tracks:", "Questi funzionano con entrambi:", "Estas funcionam com as duas faixas:", "Deze werken met beide tracks:"],
    "No single track bridges these two smoothly. Closest options (or try moving one of the tracks):": ["Ningún tema une estos dos con suavidad. Opciones más cercanas (o mueve uno de los temas):", "Aucun titre ne relie ces deux en douceur. Options les plus proches (ou déplacez un des titres) :", "Kein Track verbindet diese beiden sauber. Die nächsten Optionen (oder verschiebe einen der Tracks):", "Nessun brano collega bene questi due. Opzioni più vicine (o sposta uno dei brani):", "Nenhuma faixa liga estas duas com suavidade. Opções mais próximas (ou mova uma das faixas):", "Geen enkele track verbindt deze twee soepel. Dichtstbijzijnde opties (of verplaats een van de tracks):"],
    "These mix with both tracks:": ["Estos mezclan con ambos temas:", "Ceux-ci se mixent avec les deux :", "Diese passen zu beiden Tracks:", "Questi si mixano con entrambi:", "Estas mixam com as duas faixas:", "Deze mixen met beide tracks:"],
    "Insert": ["Insertar", "Insérer", "Einfügen", "Inserisci", "Inserir", "Invoegen"],
    "Intro": ["Intro", "Intro", "Intro", "Intro", "Intro", "Intro"],
    "Peak": ["Cumbre", "Pic", "Peak", "Picco", "Pico", "Piek"],
    "End": ["Final", "Fin", "Ende", "Fine", "Fim", "Einde"],
    "Warm": ["Calent.", "Échauf.", "Warm", "Riscald.", "Aquec.", "Warm"],
    "Hold": ["Mantener", "Tenir", "Halten", "Tenere", "Manter", "Vasthouden"],
    "Cool": ["Bajada", "Calme", "Ruhig", "Calo", "Calma", "Rustig"],
    "Tip: hold a track, then drag it to move it.": ["Consejo: mantén pulsado un tema y arrástralo para moverlo.", "Astuce : maintenez un titre puis faites-le glisser pour le déplacer.", "Tipp: Track gedrückt halten und ziehen, um ihn zu verschieben.", "Suggerimento: tieni premuto un brano e trascinalo per spostarlo.", "Dica: segure uma faixa e arraste para movê-la.", "Tip: houd een track ingedrukt en sleep hem om hem te verplaatsen."],
    "Mixes next": ["Qué sigue", "La suite", "Was passt danach", "Cosa segue", "O que mixa depois", "Wat erna mixt"],
    "Back to the top": ["Volver arriba", "Retour en haut", "Nach oben", "Torna su", "Voltar ao topo", "Terug naar boven"],
    "You have used all your credits": ["Has usado todos tus créditos", "Vous avez utilisé tous vos crédits", "Du hast alle deine Credits verbraucht", "Hai usato tutti i tuoi crediti", "Você usou todos os seus créditos", "Je hebt al je credits gebruikt"],
    "Your 2 free searches refresh in": ["Tus 2 búsquedas gratis se renuevan en", "Vos 2 recherches gratuites se renouvellent dans", "Deine 2 kostenlosen Suchen werden erneuert in", "Le tue 2 ricerche gratuite si rinnovano tra", "Suas 2 buscas grátis renovam em", "Je 2 gratis zoekopdrachten worden vernieuwd over"],
    "Your free searches have refreshed. Close this and search away!": ["Tus búsquedas gratis se han renovado. ¡Cierra esto y a buscar!", "Vos recherches gratuites sont renouvelées. Fermez ceci et cherchez !", "Deine kostenlosen Suchen sind erneuert. Schließen und loslegen!", "Le ricerche gratuite si sono rinnovate. Chiudi e cerca!", "Suas buscas grátis foram renovadas. Feche isto e busque à vontade!", "Je gratis zoekopdrachten zijn vernieuwd. Sluit dit en zoek maar raak!"],
    "Good match": ["Buena coincidencia", "Bonne correspondance", "Guter Treffer", "Buon abbinamento", "Boa combinação", "Goede match"],
    "Bad match": ["Mala coincidencia", "Mauvaise correspondance", "Schlechter Treffer", "Cattivo abbinamento", "Combinação ruim", "Slechte match"],
    "Rate this match": ["Valora esta coincidencia", "Notez cette correspondance", "Bewerte diesen Treffer", "Valuta questo abbinamento", "Avalie esta combinação", "Beoordeel deze match"],
    "Thanks - marked as a good match": ["Gracias: marcada como buena coincidencia", "Merci : marquée comme bonne correspondance", "Danke – als guter Treffer markiert", "Grazie: segnato come buon abbinamento", "Obrigado: marcada como boa combinação", "Bedankt – gemarkeerd als goede match"],
    "Thanks - marked as a bad match": ["Gracias: marcada como mala coincidencia", "Merci : marquée comme mauvaise correspondance", "Danke – als schlechter Treffer markiert", "Grazie: segnato come cattivo abbinamento", "Obrigado: marcada como combinação ruim", "Bedankt – gemarkeerd als slechte match"],
    "Rate SimilarSounds": ["Valora SimilarSounds", "Notez SimilarSounds", "SimilarSounds bewerten", "Valuta SimilarSounds", "Avalie o SimilarSounds", "Beoordeel SimilarSounds"],
    "How can we improve?": ["¿Cómo podemos mejorar?", "Comment pouvons-nous nous améliorer ?", "Was können wir besser machen?", "Come possiamo migliorare?", "Como podemos melhorar?", "Wat kunnen we verbeteren?"],
    "Tell us what would make SimilarSounds better for you": ["Cuéntanos qué haría SimilarSounds mejor para ti", "Dites-nous ce qui rendrait SimilarSounds meilleur pour vous", "Sag uns, was SimilarSounds für dich besser machen würde", "Dicci cosa renderebbe SimilarSounds migliore per te", "Diga-nos o que tornaria o SimilarSounds melhor para você", "Vertel ons wat SimilarSounds beter zou maken voor jou"],
    "Send": ["Enviar", "Envoyer", "Senden", "Invia", "Enviar", "Versturen"],
    "Your rating": ["Tu valoración", "Votre note", "Deine Bewertung", "La tua valutazione", "Sua avaliação", "Jouw beoordeling"],
    "Please choose a star rating first.": ["Elige primero una valoración con estrellas.", "Choisissez d'abord une note.", "Bitte wähle zuerst eine Sternebewertung.", "Scegli prima una valutazione.", "Escolha primeiro uma avaliação.", "Kies eerst een aantal sterren."],
    "Thank you! Your feedback has been sent.": ["¡Gracias! Tu opinión se ha enviado.", "Merci ! Votre avis a été envoyé.", "Danke! Dein Feedback wurde gesendet.", "Grazie! Il tuo feedback è stato inviato.", "Obrigado! Seu feedback foi enviado.", "Bedankt! Je feedback is verstuurd."],
    "Sorry, that didn't send. Please try again.": ["Lo sentimos, no se envió. Inténtalo de nuevo.", "Désolé, l'envoi a échoué. Réessayez.", "Das hat leider nicht geklappt. Bitte versuche es erneut.", "Spiacenti, invio non riuscito. Riprova.", "Desculpe, não foi enviado. Tente novamente.", "Sorry, verzenden is mislukt. Probeer het opnieuw."],
    "Questions": ["Preguntas", "Questions", "Fragen", "Domande", "Perguntas", "Vragen"],
    "What is SimilarSounds?": ["¿Qué es SimilarSounds?", "Qu'est-ce que SimilarSounds ?", "Was ist SimilarSounds?", "Che cos'è SimilarSounds?", "O que é o SimilarSounds?", "Wat is SimilarSounds?"],
    "A free tool for DJs. Paste a track and it finds new house music that sounds like it and mixes with it, newest releases first.": ["Una herramienta gratuita para DJs. Pega un tema y encuentra música house nueva que suena parecida y mezcla con él, empezando por los lanzamientos más recientes.", "Un outil gratuit pour les DJs. Collez un titre et il trouve de la house récente qui sonne pareil et s'enchaîne avec, en commençant par les dernières sorties.", "Ein kostenloses Tool für DJs. Füge einen Track ein und es findet neue House-Musik, die ähnlich klingt und dazu passt – neueste Releases zuerst.", "Uno strumento gratuito per DJ. Incolla un brano e trova nuova musica house che suona simile e si mixa con esso, partendo dalle uscite più recenti.", "Uma ferramenta gratuita para DJs. Cole uma faixa e ela encontra house music nova que soa parecida e mixa com ela, começando pelos lançamentos mais recentes.", "Een gratis tool voor DJ's. Plak een track en hij vindt nieuwe housemuziek die erop lijkt en ermee mixt, nieuwste releases eerst."],
    "How does it decide what mixes?": ["¿Cómo decide qué mezcla bien?", "Comment décide-t-il de ce qui s'enchaîne ?", "Wie entscheidet es, was passt?", "Come decide cosa si mixa?", "Como ele decide o que mixa?", "Hoe bepaalt het wat mixt?"],
    "Every track is analysed for its sound, musical key (shown in Camelot, like 8A), BPM and energy. Matches are ranked by how close they sound, then checked for key, tempo and energy so you can see at a glance what will blend.": ["Cada tema se analiza por su sonido, tonalidad (en Camelot, como 8A), BPM y energía. Las coincidencias se ordenan por parecido sonoro y luego se comprueban tonalidad, tempo y energía para que veas de un vistazo qué va a encajar.", "Chaque titre est analysé pour son son, sa tonalité (en Camelot, comme 8A), son BPM et son énergie. Les résultats sont classés selon leur ressemblance, puis vérifiés en tonalité, tempo et énergie pour voir d'un coup d'œil ce qui s'enchaîne.", "Jeder Track wird auf Sound, Tonart (in Camelot, z. B. 8A), BPM und Energie analysiert. Treffer werden nach Klangähnlichkeit sortiert und dann auf Tonart, Tempo und Energie geprüft, damit du sofort siehst, was passt.", "Ogni brano viene analizzato per suono, tonalità (in Camelot, come 8A), BPM ed energia. I risultati sono ordinati per somiglianza sonora e poi verificati per tonalità, tempo ed energia, così vedi subito cosa si mixa.", "Cada faixa é analisada pelo som, tom (em Camelot, como 8A), BPM e energia. Os resultados são ordenados pela semelhança e depois conferidos em tom, andamento e energia, para você ver na hora o que vai combinar.", "Elke track wordt geanalyseerd op sound, toonsoort (in Camelot, zoals 8A), BPM en energie. Matches worden gerangschikt op hoe dichtbij ze klinken en daarna gecheckt op toonsoort, tempo en energie, zodat je meteen ziet wat blendt."],
    "What can I paste in?": ["¿Qué puedo pegar?", "Que puis-je coller ?", "Was kann ich einfügen?", "Cosa posso incollare?", "O que posso colar?", "Wat kan ik plakken?"],
    "A YouTube, SoundCloud, Beatport, Bandcamp or Deezer link, or just start typing an artist and pick the track from the list.": ["Un enlace de YouTube, SoundCloud, Beatport, Bandcamp o Deezer, o empieza a escribir un artista y elige el tema de la lista.", "Un lien YouTube, SoundCloud, Beatport, Bandcamp ou Deezer, ou commencez à taper un artiste et choisissez le titre dans la liste.", "Einen YouTube-, SoundCloud-, Beatport, Bandcamp- oder Deezer-Link – oder fang an, einen Artist einzugeben, und wähl den Track aus der Liste.", "Un link di YouTube, SoundCloud, Beatport, Bandcamp o Deezer, oppure inizia a scrivere un artista e scegli il brano dall'elenco.", "Um link do YouTube, SoundCloud, Beatport, Bandcamp ou Deezer, ou comece a digitar um artista e escolha a faixa na lista.", "Een YouTube-, SoundCloud-, Beatport, Bandcamp- of Deezer-link, of begin een artiest te typen en kies de track uit de lijst."],
    "Is it free? Do I need an account?": ["¿Es gratis? ¿Necesito una cuenta?", "C'est gratuit ? Faut-il un compte ?", "Ist es kostenlos? Brauche ich ein Konto?", "È gratis? Serve un account?", "É grátis? Preciso de uma conta?", "Is het gratis? Heb ik een account nodig?"],
    "It's completely free, with no ads and no tracking, and you don't need an account. If you like, create a free one to keep your set and recent searches on every device.": ["Es totalmente gratis, sin anuncios ni rastreo, y no necesitas cuenta. Si quieres, crea una gratis para tener tu set y tus búsquedas recientes en todos tus dispositivos.", "C'est entièrement gratuit, sans pub ni pistage, et aucun compte n'est nécessaire. Si vous le souhaitez, créez-en un gratuitement pour retrouver votre set et vos recherches sur tous vos appareils.", "Komplett kostenlos, ohne Werbung und ohne Tracking – ein Konto brauchst du nicht. Wenn du willst, erstell ein kostenloses, um dein Set und deine Suchen auf allen Geräten zu haben.", "È completamente gratuito, senza pubblicità né tracciamento, e non serve un account. Se vuoi, creane uno gratis per avere set e ricerche recenti su tutti i dispositivi.", "É totalmente grátis, sem anúncios nem rastreamento, e você não precisa de conta. Se quiser, crie uma grátis para ter seu set e buscas recentes em todos os aparelhos.", "Het is helemaal gratis, zonder advertenties of tracking, en je hebt geen account nodig. Maak er desgewenst gratis een om je set en recente zoekopdrachten op al je apparaten te hebben."],
    "Why only house music?": ["¿Por qué solo house?", "Pourquoi seulement de la house ?", "Warum nur House?", "Perché solo house?", "Por que só house?", "Waarom alleen house?"],
    "Doing one genre properly beats doing everything badly. Every track in the catalogue is house - House, Deep House, Tech House, Minimal / Deep Tech and Funky / Disco House - so matches stay usable in a house set.": ["Hacer bien un género es mejor que hacerlo todo mal. Todos los temas del catálogo son house (House, Deep House, Tech House, Minimal / Deep Tech y Funky / Disco House), así que las coincidencias sirven en un set de house.", "Bien faire un seul genre vaut mieux que tout faire à moitié. Tous les titres du catalogue sont de la house (House, Deep House, Tech House, Minimal / Deep Tech et Funky / Disco House), pour des résultats jouables dans un set house.", "Ein Genre richtig zu machen ist besser, als alles halb. Jeder Track im Katalog ist House (House, Deep House, Tech House, Minimal / Deep Tech und Funky / Disco House), damit die Treffer in ein House-Set passen.", "Fare bene un solo genere è meglio che fare tutto male. Ogni brano del catalogo è house (House, Deep House, Tech House, Minimal / Deep Tech e Funky / Disco House), così i risultati funzionano in un set house.", "Fazer um gênero bem é melhor do que fazer tudo mal. Todas as faixas do catálogo são house (House, Deep House, Tech House, Minimal / Deep Tech e Funky / Disco House), então os resultados funcionam num set de house.", "Eén genre goed doen is beter dan alles half. Elke track in de catalogus is house (House, Deep House, Tech House, Minimal / Deep Tech en Funky / Disco House), zodat de matches bruikbaar blijven in een houseset."],
    "How accurate are the key and BPM?": ["¿Qué precisión tienen la tonalidad y el BPM?", "Quelle est la précision de la tonalité et du BPM ?", "Wie genau sind Tonart und BPM?", "Quanto sono precisi tonalità e BPM?", "Qual a precisão do tom e do BPM?", "Hoe nauwkeurig zijn toonsoort en BPM?"],
    "They're worked out automatically from 30-second previews, so they're good estimates rather than guarantees. Always trust your ears before you mix.": ["Se calculan automáticamente a partir de previews de 30 segundos, así que son buenas estimaciones, no garantías. Fíate siempre de tus oídos antes de mezclar.", "Ils sont calculés automatiquement à partir d'extraits de 30 secondes : ce sont de bonnes estimations, pas des garanties. Fiez-vous toujours à vos oreilles avant de mixer.", "Sie werden automatisch aus 30-Sekunden-Vorschauen ermittelt – gute Schätzungen, aber keine Garantie. Vertrau vor dem Mixen immer deinen Ohren.", "Sono calcolati automaticamente da anteprime di 30 secondi, quindi sono buone stime, non garanzie. Fidati sempre delle tue orecchie prima di mixare.", "São calculados automaticamente a partir de prévias de 30 segundos, então são boas estimativas, não garantias. Confie sempre nos seus ouvidos antes de mixar.", "Ze worden automatisch bepaald uit previews van 30 seconden, dus het zijn goede schattingen, geen garanties. Vertrouw altijd op je oren voordat je mixt."],
    "Can I download the tracks?": ["¿Puedo descargar los temas?", "Puis-je télécharger les titres ?", "Kann ich die Tracks herunterladen?", "Posso scaricare i brani?", "Posso baixar as faixas?", "Kan ik de tracks downloaden?"],
    "No. SimilarSounds doesn't host or sell music. Each match links to Beatport, Traxsource, Bandcamp, SoundCloud and YouTube so you can buy or stream it from the artist.": ["No. SimilarSounds no aloja ni vende música. Cada coincidencia enlaza a Beatport, Traxsource, Bandcamp, SoundCloud y YouTube para que la compres o escuches desde el artista.", "Non. SimilarSounds n'héberge ni ne vend de musique. Chaque titre renvoie vers Beatport, Traxsource, Bandcamp, SoundCloud et YouTube pour l'acheter ou l'écouter auprès de l'artiste.", "Nein. SimilarSounds hostet und verkauft keine Musik. Jeder Treffer verlinkt zu Beatport, Traxsource, Bandcamp, SoundCloud und YouTube, damit du ihn beim Artist kaufen oder streamen kannst.", "No. SimilarSounds non ospita né vende musica. Ogni risultato rimanda a Beatport, Traxsource, Bandcamp, SoundCloud e YouTube per acquistarlo o ascoltarlo dall'artista.", "Não. O SimilarSounds não hospeda nem vende música. Cada resultado leva ao Beatport, Traxsource, Bandcamp, SoundCloud e YouTube para você comprar ou ouvir direto do artista.", "Nee. SimilarSounds host of verkoopt geen muziek. Elke match linkt naar Beatport, Traxsource, Bandcamp, SoundCloud en YouTube, zodat je hem bij de artiest kunt kopen of streamen."],
    "How do I build a set?": ["¿Cómo armo un set?", "Comment construire un set ?", "Wie stelle ich ein Set zusammen?", "Come creo un set?", "Como monto um set?", "Hoe bouw ik een set?"],
    "Tap Add to set on any track you like, then open Your set. Drag tracks into order or press Smart order, and every transition is coloured green, amber or red so you can spot clashes. Share the set with a link.": ["Toca Añadir al set en los temas que te gusten y abre Tu set. Arrástralos para ordenarlos o pulsa Orden inteligente: cada transición se colorea en verde, ámbar o rojo para detectar choques. Comparte el set con un enlace.", "Touchez Ajouter au set sur les titres qui vous plaisent, puis ouvrez Votre set. Faites-les glisser ou appuyez sur Ordre intelligent : chaque transition est colorée en vert, orange ou rouge pour repérer les clashs. Partagez le set avec un lien.", "Tippe bei Tracks, die dir gefallen, auf Zum Set hinzufügen und öffne dann Dein Set. Zieh sie in die richtige Reihenfolge oder drück Smarte Reihenfolge – jeder Übergang wird grün, gelb oder rot markiert. Teile das Set per Link.", "Tocca Aggiungi al set sui brani che ti piacciono, poi apri Il tuo set. Trascinali in ordine o premi Ordine intelligente: ogni passaggio è colorato di verde, giallo o rosso per vedere i conflitti. Condividi il set con un link.", "Toque em Adicionar ao set nas faixas que você gostar e abra Seu set. Arraste para ordenar ou toque em Ordem inteligente: cada transição fica verde, âmbar ou vermelha para você ver os choques. Compartilhe o set com um link.", "Tik op Toevoegen aan set bij tracks die je goed vindt en open Je set. Sleep ze op volgorde of druk op Slimme volgorde: elke overgang wordt groen, oranje of rood, zodat je botsingen ziet. Deel de set met een link."],
    "These pages are only available in English.": ["Estas páginas solo están disponibles en inglés.", "Ces pages ne sont disponibles qu'en anglais.", "Diese Seiten gibt es nur auf Englisch.", "Queste pagine sono disponibili solo in inglese.", "Estas páginas estão disponíveis apenas em inglês.", "Deze pagina's zijn alleen in het Engels beschikbaar."],
  };

  // ---------- HTML fragments with inner elements kept in place ({1}, {2}… = the original child elements)
  const H = {
    hero2: ["Consigue {1}.", "Obtenez {1}.", "Hol dir {1}.", "Ottieni {1}.", "Consiga {1}.", "Krijg {1}."],
    emptySet: ["Busca un tema, toca {1} en los que te gusten y arrástralos para ordenarlos.", "Cherchez un titre, touchez {1} sur ceux qui vous plaisent et faites-les glisser dans l'ordre.", "Such einen Track, tippe bei den gewünschten auf {1} und zieh sie in die richtige Reihenfolge.", "Cerca un brano, tocca {1} su quelli che ti piacciono e trascinali in ordine.", "Busque uma faixa, toque em {1} nas que você gostar e arraste-as para ordenar.", "Zoek een track, tik op {1} bij de tracks die je leuk vindt en sleep ze op volgorde."],
    colourKey: ["Cada par recibe un color: {1} mezcla bien, {2} es aceptable, {3} chocará.", "Chaque paire a une couleur : {1} s'enchaîne bien, {2} est jouable, {3} va clasher.", "Jedes Paar bekommt eine Farbe: {1} passt gut, {2} ist machbar, {3} kollidiert.", "Ogni coppia ha un colore: {1} si mixa bene, {2} è accettabile, {3} stonerà.", "Cada par recebe uma cor: {1} mixa bem, {2} é aceitável, {3} vai chocar.", "Elk paar krijgt een kleur: {1} mixt goed, {2} is werkbaar, {3} botst."],
    gate: ["Esto carga el reproductor de {1}, que puede usar sus propias cookies. {2} · {3}", "Ceci charge le lecteur de {1}, qui peut déposer ses propres cookies. {2} · {3}", "Hier wird der Player von {1} geladen, der eigene Cookies setzen kann. {2} · {3}", "Questo carica il player di {1}, che può impostare i propri cookie. {2} · {3}", "Isto carrega o player do {1}, que pode definir seus próprios cookies. {2} · {3}", "Dit laadt de speler van {1}, die eigen cookies kan plaatsen. {2} · {3}"],
    uploaded: ["Subido por {1} en", "Mis en ligne par {1} sur", "Hochgeladen von {1} auf", "Caricato da {1} su", "Enviado por {1} no", "Geüpload door {1} op"],
    videofrom: ["Vídeo de {1} en", "Vidéo de {1} sur", "Video von {1} auf", "Video di {1} su", "Vídeo de {1} no", "Video van {1} op"],
    acctFine: ["Al crear una cuenta aceptas nuestros {1} y nuestra {2}.", "En créant un compte, vous acceptez nos {1} et notre {2}.", "Mit dem Erstellen eines Kontos stimmst du unseren {1} und unserer {2} zu.", "Creando un account accetti i nostri {1} e la nostra {2}.", "Ao criar uma conta você aceita nossos {1} e nossa {2}.", "Door een account aan te maken ga je akkoord met onze {1} en ons {2}."],
    acctAs: ["Has iniciado sesión como {1}. Tu set y tus búsquedas recientes se guardan en tu cuenta.", "Connecté en tant que {1}. Votre set et vos recherches récentes sont enregistrés dans votre compte.", "Angemeldet als {1}. Dein Set und deine letzten Suchen werden in deinem Konto gespeichert.", "Accesso come {1}. Il tuo set e le ricerche recenti sono salvati nel tuo account.", "Conectado como {1}. Seu set e suas buscas recentes ficam salvos na sua conta.", "Ingelogd als {1}. Je set en recente zoekopdrachten worden in je account bewaard."],
    pwGet: ["¿No puedes esperar? Consigue búsquedas ilimitadas con {1}.", "Pas envie d'attendre ? Recherches illimitées avec {1}.", "Keine Lust zu warten? Unbegrenzt suchen mit {1}.", "Non vuoi aspettare? Ricerche illimitate con {1}.", "Não quer esperar? Tenha buscas ilimitadas com o {1}.", "Geen zin om te wachten? Onbeperkt zoeken met {1}."],
    sharedNote: ["Estás viendo una búsqueda compartida de {1}.", "Vous consultez une recherche partagée pour {1}.", "Du siehst eine geteilte Suche für {1}.", "Stai guardando una ricerca condivisa per {1}.", "Você está vendo uma busca compartilhada de {1}.", "Je bekijkt een gedeelde zoekopdracht voor {1}."],
    tip1: ["Empieza a escribir el {1} y elige el tema de la lista: es lo más fiable.", "Commencez à taper le {1} et choisissez le titre dans la liste : c'est le plus fiable.", "Fang an, den {1} einzugeben, und wähl den Track aus der Liste – das ist am zuverlässigsten.", "Inizia a scrivere il {1} e scegli il brano dall'elenco: è il modo più affidabile.", "Comece a digitar o {1} e escolha a faixa na lista: é o jeito mais confiável.", "Begin met het typen van de {1} en kies de track uit de lijst – dat werkt het best."],
    tip2: ["Revisa la ortografía o usa el formato {1}.", "Vérifiez l'orthographe ou utilisez le format {1}.", "Prüf die Schreibweise oder nutze das Format {1}.", "Controlla l'ortografia o usa il formato {1}.", "Confira a grafia ou use o formato {1}.", "Controleer de spelling of gebruik het formaat {1}."],
  };

  // ---------- patterns for text that contains numbers or names ($1, $2 … = captured parts)
  const P = [
    [/^That's every match with your filters \((\d+)\)\. Want more\?$/, ["Son todas las coincidencias con tus filtros ($1). ¿Quieres más?", "Ce sont toutes les correspondances avec vos filtres ($1). Vous en voulez plus ?", "Das sind alle Treffer mit deinen Filtern ($1). Mehr?", "Sono tutti i risultati con i tuoi filtri ($1). Ne vuoi altri?", "São todas as correspondências com seus filtros ($1). Quer mais?", "Dat zijn alle matches met je filters ($1). Meer?"]],
    [/^Released in the last (\d+) days and mixes with tracks in your set\.$/, ["Lanzados en los últimos $1 días y mezclan con temas de tu sesión.", "Sortis ces $1 derniers jours et se mixent avec les titres de ton set.", "In den letzten $1 Tagen erschienen und passt zu Tracks in deinem Set.", "Usciti negli ultimi $1 giorni e si mixano con i brani del tuo set.", "Lançadas nos últimos $1 dias e mixam com faixas do seu set.", "Uitgebracht in de laatste $1 dagen en mixt met nummers in je set."]],
    [/^Planned (\d+) tracks$/, ["$1 temas planificados", "$1 titres planifiés", "$1 Tracks geplant", "$1 brani pianificati", "$1 faixas planejadas", "$1 nummers gepland"]],
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
    [/^(.+), signed in - open your account$/, ["$1, sesión iniciada: abrir tu cuenta", "$1, connecté : ouvrir votre compte", "$1, angemeldet – Konto öffnen", "$1, connesso: apri il tuo account", "$1, conectado: abrir sua conta", "$1, ingelogd – open je account"]],
    [/^Try for free now: (.+)$/, ["Pruébalo gratis ya: $1", "Essayez gratuitement : $1", "Jetzt kostenlos testen: $1", "Provalo gratis ora: $1", "Experimente grátis agora: $1", "Probeer nu gratis: $1"]],
    [/^(\d+) free searches left$/, ["Te quedan $1 búsquedas gratis", "Il vous reste $1 recherches gratuites", "Noch $1 kostenlose Suchen", "Ti restano $1 ricerche gratuite", "Restam $1 buscas grátis", "Nog $1 gratis zoekopdrachten"]],
    [/^(.+) · each new track uses 1$/, ["$1 · cada tema nuevo usa 1", "$1 · chaque nouveau titre en utilise 1", "$1 · jeder neue Track verbraucht 1", "$1 · ogni nuovo brano ne usa 1", "$1 · cada faixa nova usa 1", "$1 · elke nieuwe track kost er 1"]],
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
    [/^Your key is (\S+)\. Keys outlined in white mix with it\. Tap a key to show only those matches\.$/, ["Tu tonalidad es $1. Las tonalidades con borde blanco mezclan con ella. Toca una para ver solo esas coincidencias.", "Votre tonalité est $1. Les tonalités entourées de blanc s'enchaînent avec. Touchez-en une pour n'afficher que celles-ci.", "Deine Tonart ist $1. Weiß umrandete Tonarten passen dazu. Tippe auf eine, um nur diese Treffer zu zeigen.", "La tua tonalità è $1. Le tonalità bordate di bianco si mixano con essa. Toccane una per vedere solo quei risultati.", "Seu tom é $1. Os tons com contorno branco mixam com ele. Toque em um para ver só esses resultados.", "Jouw toonsoort is $1. Wit omrande toonsoorten mixen ermee. Tik op een toonsoort om alleen die matches te zien."]],
    [/^(\d+[AB]): (\d+) tracks$/, ["$1: $2 temas", "$1 : $2 titres", "$1: $2 Tracks", "$1: $2 brani", "$1: $2 faixas", "$1: $2 tracks"]],
    [/^Showing (\d+) in (\d+[AB])$/, ["Mostrando $1 en $2", "$1 affichés en $2", "$1 in $2 angezeigt", "$1 mostrati in $2", "Mostrando $1 em $2", "$1 getoond in $2"]],
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
  const SKIP = ".acct-name.is-user, #acct-email, .t, .a, .qt, .tt, .ta, .sg-name, .sg-sub, .logo, .brand, .chip.cam, .group-n, script, style, code, kbd, [data-no-i18n]";
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
  let titleSrc = null, titleOut = null;
  function translateTitle() {
    const cur = document.title;
    if (cur !== titleOut) titleSrc = cur;          // the page set a new (English) title
    titleOut = tr(titleSrc);
    if (document.title !== titleOut) document.title = titleOut;
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
