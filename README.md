# PodLoop
Progetto di tecnologie web di Adam Taoufiq

Per una descrizione dettagliata del progetto, si prega di visionare il file **podloop_tesina.pdf**
# Requsiti

I requisiti per far pratire il progetto sono:

- Python >= 3.9 
- I moduli all'interno del file **requirements.txt**

# Avviare il progetto

Il progetto parte con dei dati iniziali in modo da non avere un sito vuoto, per farlo partire seguire i seguenti passi

- Aprire il terminale ed entrare nella cartella del progetto
- Inserire il comando  `pipenv shell`
- Entrare nella cartella **podloop**
- Inserire il comando `python.exe .\manage.py runserver`
- A questo punto navigare all'url http://127.0.0.1:8000/

All'interno del file users.json che si trova in **podloop/core/data** si possono scegliere vari utenti con il quale eseguire l'accesso, oppure se si preferisce ci si può registrare con un account nuovo. Alcuni utenti hanno anche dei podcast, con questo si possono vedere le feature specifiche per i creatori di contenuti e quelle per gli utenti normali o anonimi.

Una volta fatto l'accesso si può navigare nel sito, iscriversi a podcast, ascoltare episodi commentare ecc..
# Eliminare i dati nelle tabelle

Nel caso si volesse ripartire da un database vuoto, si può eseguire il drop di tutte le tabelle popolate eseguendo il seguente script.

Basta andare nel file del database **db.sqlite3**, selezionare l'editor sql, incollare le seguenti istruzioni ed eseguirle.

Inoltre se si vogliono anche eliminare i veecchi file immagine e audio, eliminare tutti i file di **podloop/media/audios** e tutti gli elementi della cartella **podloop/media/images** **tranne la cartella default**
```sql
DELETE FROM "accounts_user";

DELETE FROM "core_episodecomment";

DELETE FROM "core_episodestream";

DELETE FROM "core_episodecommentlike";

DELETE FROM "core_episodelike";

DELETE FROM "core_playlist_episodes";

DELETE FROM "core_playlist";

DELETE FROM "core_episode";

DELETE FROM "core_podcastfollow";

DELETE FROM "core_podcast_categories";

DELETE FROM "core_podcast";
```
