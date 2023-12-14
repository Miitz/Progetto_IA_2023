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

### Esempio di utilizzo
```bash
python runner.py "huric/it/_file_.huric"
```
