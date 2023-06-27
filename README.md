# podloop-project

Project for my third year Tecnologie Web class

# Eliminare i dati nelle tabelle

Nel caso si volesse ripartire da un database vuoto, si può eseguire il drop di tutte le tabelle popolate eseguendo il seguente script.

Basta andare nel file del database db.sqlite3, selezionare l'editor sql e incollare le seguenti istruzioni.

```sql
DELETE FROM "accounts_user";

DELETE FROM "core_episodecomment";

DELETE FROM "core_episodecommentlike";

DELETE FROM "core_episodelike";

DELETE FROM "core_playlist_episodes";

DELETE FROM "core_playlist";

DELETE FROM "core_episode";

DELETE FROM "core_podcastfollow";

DELETE FROM "core_podcast_categories";

DELETE FROM "core_podcast";
```
