# Detective Game
Ein Projekt im Rahmen des Game Programming Seminars am HPI im Wintersemester 2019.

Dieses Readme beschreibt das gesamte Projekt und enthält außerdem die Beschreibung und Installationsanleitung der Serverkomponente (siehe 'Server')

## Introduction
Im Rahmen dieses Seminars soll anhand von Spielprototypen demonstriert werden, wie Technologien missbraucht werden können. Wir versuchen in diesem Prototypen weitreichende Berechtigungen auf dem Smartphone des Spielers zu erlangen, um die gespielte Krimigeschichte adaptiv auf den Spieler anzupassen. Außerdem möchten wir die Grenze zwischen dem Spiel und der Realität des Spielers verwischen. Letztendlich möchten wir genug emotionale Bindung des Spielers erzeugen, um ihn zu Aktionen im echten Leben zu bewegen, wie z.B. Besuchen von (ungewöhnlichen) Orten, Aufstehen zu ungewöhnlichen Zeiten, das freiwillige Liefern von weitern Bild/Ton/Standortdaten.

## Storyline
Der Spieler übernimmt die Rolle eines frisch beförderten Kommissars. Er erhält von seinem Vorgesetzten Hauptkommissar Anweisungen. Diese erfüllt er mithilfe der App, um sich in der Story voranzuspielen.

## Requirements
- Ein Smartphone (Minimale Android Version 23)
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
It is recommended to use a virtual environment
``` bash
virtualenv --python=python3 .venv
source .venv/bin/activate
```

- Use `./manage.sh install` to install and setup the server
- Use `./manage.sh start` to start the server
- For more commands use `./manage.sh help`

## FAQ
- *Warum benutzen wir Telegram und simulieren die Kommunikation nicht auch in der App?*  
Da Telegram das Hauptkommunikationsmittel am HPI ist, hoffen wir durch das Integrieren dieser Plattform die Grenzen zwischen dem Programm und echten Personen zu verwischen (indem der Botaccount zwischen echten Kontakten auftaucht, die Nachrichten von echten Menschen und die des Bots in einer Push-Notification stehen, usw.). Außerdem spart uns diese Entscheidung die Arbeit an einem Chatprogramm, welche für einen Prototypen nicht notwendig ist.
- *Warum heißt der Bot "AndyAbbot"?  
Weil Telegram Bots auf "bot" enden müssen, und wir einen möglichst menschlichen Eindruck vermitteln wollen, um eine höhere Bindung aufzubauen. "Andy" ist einfach ein häufiger Name und außerdem eine Alliteration
