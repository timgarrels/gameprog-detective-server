# Detective Game
Ein Projekt im Rahmen des Game Programming Seminars am HPI im Wintersemester 2019.

Dieses Readme beschreibt das gesamte Projekt und enthält außerdem die Beschreibung und Installationsanleitung der Serverkomponente (siehe 'Server')

## Introduction
Im Rahmen dieses Seminars soll anhand von Spielprototypen demonstriert werden, wie Technologien missbraucht werden können. Wir versuchen in diesem Prototypen weitreichende Berechtigungen auf dem Smartphone des Spielers zu erlangen, um die gespielte Krimigeschichte adaptiv auf den Spieler anzupassen. Außerdem möchten wir die Grenze zwischen dem Spiel und der Realität des Spielers verwischen. Letztendlich möchten wir genug emotionale Bindung des Spielers erzeugen, um ihn zu Aktionen im echten Leben zu bewegen, wie z.B. Besuchen von (ungewöhnlichen) Orten, Aufstehen zu ungewöhnlichen Zeiten, das freiwillige Liefern von weitern Bild/Ton/Standortdaten.

## Storyline
Der Spieler nimmt die Rolle eines Kriminaldetektivs ein. Er ermittelt in einem Mordfall. Er verfügt eine Software, die ihm verschiedene menschliche Quellen vermittelt. Mit diesen Quellen kommuniziert er über ein Chatprogramm. Er kann Fragen stellen, Antworten geben und muss Aktionen unternehmen um einerseits seinen Fall zu lösen, andererseits aber auch die Sicherheit der Quelle selbst und das Vertrauen der Quelle in ihn zu wahren.

## Requirements
- Ein Smartphone (TODO: Android Version?)
- Eine Telegram-Account

## Softwarekomponenten
Die Software besteht aus 3 Hauptkomponenten, der quellenvermittelnden App (im Folgenden "App" genannt), dem quellensimulierenden Chatbot (im Folgenden "Bot" genannt) und dem orchestrierendem Server (im Folgenden "Server" genannt).

![First Architecture Draft](/docs/basic_architecture.jpeg)

### App
Diese App ist der Hauptdatensammler des Spiels. Da wir über die Telegram-API nur an sehr begrenzte Daten kommen, versuchen wir mit dieser App an Berechtigungen auf dem Smartphone des Spielers zu erlangen. Die aus solchen Berechtigungen resultierenden Daten können wir dann über das Internet teilen und anhand dieser Daten das Verhalten des Bots anpassen.  
Die App muss vom Spieler heruntergeladen werden, um den Telegram-Chat mit dem Bot zu starten (dabei wird ein Schlüssel übermittelt, damit die gesammelten Daten der App mit einem Telegram-User korreliert werden können). 
Außerdem planen wir, über die App den "Sicherheitsstatus" und das "Vertrauenslevel" der Quelle anzuzeigen.

TODO: Link zum Repo der App

### Bot
Der Telegram-Bot simuliert die Kommunikation der Quelle mit dem Spieler. Über ihn wird die (adaptive) Spielgeschichte erzählt und die Aufgaben der Quelle an den Spieler kommuniziert.

TODO: Link zum Repo des Bots

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

## Arbeitsetappen
Um die ersten Schritte für unser Projekt zu machen implementieren wir den Handshake App -> Server -> Bot -> Server um den neuen User auf dem Server zu registrieren und die App Daten mit dem Telegramaccount assoziieren zu können. 
![TOP0](/docs/top0.jpeg)
Anschließend möchten wir bereits einen Geschichtsprototypen haben: Der Bot soll eine lineare Geschichte erzählen können, die mithilfe von Buttons gesteuert werden kann. Diese Geschichte soll hardgecoded personalisiert werden können. Diese Personalisierung soll durch die erste Abhörfunktion der App realisiert werden: Das Stehlen von Kontakdaten. Des Weiteren soll die Apps entdeckte Clues speichern und anzeigen zu können.
![TOP1](/docs/top1.jpeg)

## FAQ
- *Warum benutzen wir Telegram und simulieren die Quellenkommunikation nicht auch in der App?*  
Da Telegram das Hauptkommunikationsmittel am HPI ist, hoffen wir durch das Integrieren dieser Plattform die Grenzen zwischen dem Programm und echten Personen zu verwischen (indem der Botaccount zwischen echten Kontakten auftaucht, die Nachrichten von echten Menschen und die des Bots in einer Push-Notification stehen, usw.). Außerdem spart uns diese Entscheidung die Arbeit an einem Chatprogramm, welche für einen Prototypen nicht notwendig ist.
- *Warum heißt der Bot "AndyAbbot"?  
Weil Telegram Bots auf "bot" enden müssen, und wir einen möglichst menschlichen Eindruck vermitteln wollen, um eine höhere Bindung aufzubauen. "Andy" ist einfach ein häufiger Name und außerdem eine Alliteration
