# Detective Game
Ein Projekt im Rahmen des Game Programming Seminars am HPI im Wintersemester 2019

## Introduction
Im Rahmen dieses Seminars soll anhand von Spielprototypen demonstriert werden, wie Technologien missbraucht werden können. Wir versuchen in diesem Prototypen weitreichende Berechtigungen auf dem Smartphone des Spielers zu erlangen, um die gespielte Krimigeschichte adaptiv auf den Spieler anzupassen. Außerdem möchten wir die Grenze zwischen dem Spiel und der Realität des Spielers verwischen. Letztendlich möchten wir genug emotionale Bindung des Spielers erzeugen, um ihn zu Aktionen im echten Leben zu bewegen, wie z.B. Besuchen von (ungewöhnlichen) Orten, Aufstehen zu ungewöhnlichen Zeiten, das freiwillige Liefern von weitern Bild/Ton/Standortdaten.

## Storyline
Der Spieler nimmt die Rolle eines Kriminaldetektivs ein. Er ermittelt in einem Mordfall. Er verfügt eine Software, die ihm verschiedene menschliche Quellen vermittelt. Mit diesen Quellen kommuniziert er über ein Chatprogramm. Er kann Fragen stellen, Antworten geben und muss Aktionen unternehmen um einerseits seinen Fall zu lösen, andererseits aber auch die Sicherheit der Quelle selbst und das Vertrauen der Quelle in ihn zu wahren.

## Softwarekomponenten
Die Software besteht aus 2 Hauptkomponenten, der quellenvermittelnden App (im Folgenden "App" genannt) und dem quellensimulierenden Chatbot (im Folgenden "Bot" genannt)

### App
Diese App ist der Hauptdatensammler des Spiels. Da wir über die Telegram-API nur an sehr begrenzte Daten kommen, versuchen wir mit dieser App an Berechtigungen auf dem Smartphone des Spielers zu erlangen. Die aus solchen Berechtigungen resultierenden Daten können wir dann über das Internet teilen und anhand dieser Daten das Verhalten des Bots anpassen.  
Die App muss vom Spieler heruntergeladen werden, um den Telegram-Chat mit dem Bot zu starten (dabei wird ein Schlüssel übermittelt, damit die gesammelten Daten der App mit einem Telegram-User korreliert werden können). 
Außerdem planen wir, über die App den "Sicherheitsstatus" und das "Vertrauenslevel" der Quelle anzuzeigen.

### Bot
Der Telegram-Bot simuliert die Kommunikation der Quelle mit dem Spieler. Über ihn wir sowohl die (adaptive) Spielgeschichte selbst erzählt als auch die Aufgaben der Quelle an den Spieler kommuniziert.


## FAQ
- *Warum benutzen wir Telegram und simulieren die Quellenkommunikation nicht auch in der App?*  
Da Telegram das Hauptkommunikationsmittel am HPI ist, hoffen wir durch das Integrieren dieser Plattform die Grenzen zwischen dem Programm und echten Personen zu verwischen (indem der Botaccount zwischen echten Kontakten auftaucht, die Nachrichten von echten Menschen und die des Bots in einer Push-Notification stehen, usw.). Außerdem spart uns diese Entscheidung die Arbeit an einem Chatprogramm, welche für einen Prototypen nicht notwendig ist.
- *Warum heißt der Bot "AndyAbbot"?  
Weil Telegram Bots auf "bot" enden müssen, und wir einen möglichst menschlichen Eindruck vermitteln wollen, um eine höhere Bindung aufzubauen. "Andy" ist einfach ein häufiger Name und außerdem eine Alliteration
