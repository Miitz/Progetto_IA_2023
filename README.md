<h1 align="center">
  🤖 Supporto grafico per la navigazione robotica
</h1>
<h3 align="center">🏘️ <em>Creazione di ambienti virtuali ottimizzati per la navigazione robotica</em></h3>

La procedura principale implica l'analisi di file del tipo <a href="https://github.com/crux82/huric">HURIC (Human-Robot Interaction Corpus)</a> al fine di estrarre dati rilevanti.
I dati vengono poi processati attraverso il framework Procthor, costruito su AI2Thor, che li converte in una rappresentazione JSON dettagliata e strutturata dell'ambiente fisico corrispondente.
Questa rappresentazione è specificatamente progettata per facilitare analisi avanzate e interazioni efficaci nelle applicazioni di robotica e intelligenza artificiale.

Esempi di file HURIC utilizzati in questo processo sono accessibili e possono essere esaminati tramite il seguente collegamento: https://github.com/crux82/huric/tree/master/it.


## 💻 Installazione
Clonare la repository
```bash
git clone https://github.com/Miitz/progetto_IA_2023.git
```
### Ambiente virtuale
Installare il package `virtualenv`
```bash
pip install virtualenv
```
Creare un ambiente virtuale all'interno della cartella progetto
```bash
python -m venv nome_ambiente
```
Attivare l'ambiente virtuale
* `Linux/MacOS`
  
  ```bash
  source nome_ambiente/bin/activate
  ```
* `Windows`
  
  ```powershell
  nome_ambiente\bin\Activate.ps1
  ```
### Installazione dei requisiti
Lista dei package necessari -> `requirements.txt`
```bash
pip install -r requirements.txt
```

### Utilizzo
Generazione del file JSON con descrizione dell'ambiente senza immagini
```bash
python runner.py "huric/it/_file_.huric"
```
Generazione completa del file JSON con descrizione dell'ambiente e immagini utilizzando la flag `--visualize` o `-v`
```bash
python runner.py --visualize "huric/it/_file_.huric"
```
Per ogni file HuRIC generato utuilizzando la flag `--visualize` o `-v` verrà creata una cartella di questo tipo:
    
    huric_file                                          # Cartella generale file HuRIC
    ├── images                                          # Cartella principale contenente le immagini dell'ambiente
    │   ├── example_room                                # Cartella generata per ogni stanza dell'ambiente
    │   │   ├── bounding_box                            # Cartella contenente immagini con bounding_box
    │   │   │   ├── position_0                          # Cartella contenente le immagini generate in posizione 0
    │   │   │   │   ├── image_bounding_box_pos_0_0.jpg
    │   │   │   │   └── ...
    │   │   │   ├── position_1                          # Cartella contenente le immagini generate in posizione 1
    │   │   │   │   └── ...
    │   │   │   └── ...
    │   │   └── normal                                  # Cartella contenente immagini senza bounding_box
    │   │       ├── position_0
    │   │       │   ├── image_pos_0_0.jpg
    │   │       │   └── ...
    │   │       ├── position_1
    │   │       │   └── ...
    │   │       └── ...
    │   ├── positions.jpg                               # Immagine delle posizioni raggiungibili dal robot
    │   └── top_down.png                                # Immagine aerea dell'ambiente
    ├── huric_file.hrc                                  # File HuRIC in input
    └── gen_huric_file.json                             # File JSON in output con descrizione dell'ambiente e immagini
