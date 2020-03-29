# Detective Game
Ein Projekt im Rahmen des Game Programming Seminars am HPI im Wintersemester 2019.

Dieses Readme beschreibt das gesamte Projekt und enthält außerdem die Beschreibung und Installationsanleitung der Serverkomponente (siehe 'Server').  
Dieses Repo enthält einerseits den Code der Serverkomponente (siehe 'Server') und außerdem das [Wiki](https://github.com/EatingBacon/gameprog-detective-server/wiki) unseres Projekts.

## Einführung
Im Rahmen dieses Seminars soll anhand von Spielprototypen demonstriert werden, wie Technologien missbraucht werden können. Wir versuchen in diesem Prototypen weitreichende Berechtigungen auf dem Smartphone des Spielers zu erlangen, um die gespielte Krimigeschichte adaptiv auf den Spieler anzupassen. Außerdem möchten wir die Grenze zwischen dem Spiel und der Realität des Spielers verwischen. Letztendlich möchten wir genug emotionale Bindung des Spielers erzeugen, um ihn zu Aktionen im echten Leben zu bewegen, wie z.B. Besuchen von (ungewöhnlichen) Orten, Aufstehen zu ungewöhnlichen Zeiten, das freiwillige Liefern von weitern Bild/Ton/Standortdaten.

## Storyline
Der Spieler übernimmt die Rolle eines frisch beförderten Kommissars. Er erhält von seinem Vorgesetzten Hauptkommissar Anweisungen. Diese erfüllt er mithilfe der App, um sich in der Story voranzuspielen.

## Requirements
- Ein Smartphone (Minimale Android API Version 23)
- Eine Telegram-Account

## Softwarekomponenten
Die Software besteht aus 3 Hauptkomponenten, der datensammelnden App (im Folgenden "App" genannt), dem Chatbot (im Folgenden "Bot" genannt) und dem orchestrierendem Server (im Folgenden "Server" genannt).

![Game Architecture](/docs/gameprog_architecture.png)

### App
Diese App ist der Hauptdatensammler des Spiels. Da wir über die Telegram-API nur an sehr begrenzte Daten kommen, versuchen wir mit dieser App an Berechtigungen auf dem Smartphone des Spielers zu erlangen. Die aus solchen Berechtigungen resultierenden Daten können wir dann über das Internet teilen und anhand dieser Daten das Verhalten des Bots anpassen.  
Die App muss vom Spieler heruntergeladen werden, um den Telegram-Chat mit dem Bot zu starten (dabei wird ein Schlüssel übermittelt, damit die gesammelten Daten der App mit einem Telegram-User korreliert werden können). 

[Link zum Repo der App](https://github.com/ADimeo/gameprog-detective-app)

### Bot
Der Telegram-Bot simuliert die Kommunikation des Hauptkommissars mit dem Spieler. Über ihn wird die (adaptive) Spielgeschichte erzählt und die Aufgaben des Hauptkommissars an den Spieler kommuniziert.

[Link zum Repo des Bots](https://github.com/EatingBacon/gameprog-detective-bot)

### Server
Der Server bietet sowohl für die App als auch für den Bot die notwendigen API Endpunkte. Er erhält Daten von der App und speichert und analysiert diese. Er liefert dem Bot die Story, bereits personalisiert für den jeweiligen User. Dafür verwaltet der Server sowohl die Grundstory als auch die Userdaten (persönliche Daten und story-relevante Daten wie aktuellen Spielstand).

Der Source-Code und Dokumentation des Servers ist in diesem Repo zu finden.

#### Install and Start
Voraussetzung ist ein Linux System mit installiertem python 3.8
1. `./manage.sh install` um den Server zu installieren
1. `./manage.sh start` um den Server zu starten
1. für weitere Befehle `./manage.sh help` benutzen
1. siehe [Bot Repo](https://github.com/EatingBacon/gameprog-detective-bot) für Installation und Start des Bots
1. nach Start von Server und Bot kann die App und damit das Spiel gestartet werden

#### Architektur-Überblick
Der Server wird durch eine Flask App (`/app`) implementiert. Diese verwaltet verschiedene API-Endpunkte (`/app/routes`). Außerdem wird eine Datenbank verwaltet. Deren ORM wird in `/app/models` implementiert. Der Story-Inhalt und der Story-verwaltende Code liegt unter `/app/story`.  

#### Nutzung ohne App
Unsere App ist sehr datenhungrig. Um das Spiel zu testen, ohne die App zu installieren, haben wir ein Postman package erstellt. Dieses immitiert die App. Damit lässt sich das Spiel auch ohne Appnutzung durchspielen (die Spielerfahrung leidet darunter jedoch deutlich). Die Nutzung ist wie folgt:
1. `detective-game-no-app-walkthrough.json` mit Postman importieren
1. `create user` senden, um einen neuen Nutzer zu erstellen
1. die URL aus der response öffnen, um den Chat mit Kommissar Rex zu starten
1. `send mocked contacts` senden, um das Stehlen von Kontakten für "Personalisierung" zu mocken
1. Die Story spielen und neue Tasks in den folgenden **zwei**  Schritten erfüllen:
   1. die Request für den entsprechenden Task senden
   2. `TASK FINISHED request check` senden, um die serverseitige Validierung anzufragen
1. Es finden sich außerdem weitere Debug-Methoden im Package, die das Testen weiter erleichtern

## FAQ
- *Warum benutzen wir Telegram und simulieren die Kommunikation nicht auch in der App?*  
Da Telegram das Hauptkommunikationsmittel am HPI ist, hoffen wir durch das Integrieren dieser Plattform die Grenzen zwischen dem Programm und echten Personen zu verwischen (indem der Botaccount zwischen echten Kontakten auftaucht, die Nachrichten von echten Menschen und die des Bots in einer Push-Notification stehen, usw.). Außerdem spart uns diese Entscheidung die Arbeit an einem Chatprogramm, welche für einen Prototypen nicht notwendig ist.
- *Warum heißt der Bot "AndyAbbot"?  
Weil Telegram Bots auf "bot" enden müssen, und wir einen möglichst menschlichen Eindruck vermitteln wollen, um eine höhere Bindung aufzubauen. "Andy" ist einfach ein häufiger Name und außerdem eine Alliteration
Wir haben uns später jedoch entschieden, den Namen des Bots zu "Kommisssar Rex" umzubenennen
