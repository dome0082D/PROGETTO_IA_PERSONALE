import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'dart:convert';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark(useMaterial3: true),
      home: const MonitorPage(),
    );
  }
}

class MonitorPage extends StatefulWidget {
  const MonitorPage({super.key});
  @override
  State<MonitorPage> createState() => _MonitorPageState();
}

class _MonitorPageState extends State<MonitorPage> {
  late WebSocketChannel channel;
  final FlutterTts flutterTts = FlutterTts();
  final TextEditingController _inputController = TextEditingController();
  
  // VARIABILI DI STATO PERSISTENTI
  String sicurezza = "OPERATIVO";
  double cpuValue = 0.0;
  String ultimaLettura = ""; 
  Map<String, dynamic> ultimiDatiVisuali = {
    "tipo": "TESTO", 
    "contenuto": "SIA Connessa. In attesa di comandi..."
  };
  
  bool haErroreConnessione = false;

  @override
  void initState() {
    super.initState();
    initWebSocket();
    initTts();
  }

  void initWebSocket() {
    try {
      // Connessione al server SIA
      channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8080'));
      
      // Ascolto continuo del flusso dati in background
      channel.stream.listen(
        (message) {
          elaboraMessaggioInArrivo(message);
        },
        onError: (error) {
          setState(() {
            haErroreConnessione = true;
          });
        },
        onDone: () {
          debugPrint("Connessione WebSocket chiusa.");
        },
      );
    } catch (e) {
      setState(() {
        haErroreConnessione = true;
      });
    }
  }

  void initTts() async {
    await flutterTts.setLanguage("it-IT");
    await flutterTts.setSpeechRate(0.5);
  }

  void elaboraMessaggioInArrivo(dynamic message) {
    try {
      Map<String, dynamic> dati = jsonDecode(message);
      
      setState(() {
        // 1. Aggiorna sempre lo stato globale della sicurezza se presente
        if (dati.containsKey('sicurezza')) {
          sicurezza = dati['sicurezza']?.toString() ?? 'OPERATIVO';
        }
        
        // 2. Se è un pacchetto di monitoraggio aggiorna solo i dati hardware senza cancellare lo schermo
        if (dati.containsKey('monitoraggio')) {
          final mon = dati['monitoraggio'];
          if (mon is Map && mon.containsKey('cpu')) {
            cpuValue = (mon['cpu'] ?? 0.0).toDouble();
          }
        }
        
        // 3. Se contiene un contenuto visivo reale (diverso da MONITOR), aggiorna la visualizzazione centrale
        String? tipo = dati['tipo'];
        if (tipo != null && tipo != 'MONITOR') {
          ultimiDatiVisuali = dati;
          gestisciTts(dati); // Riproduzione vocale sicura all'arrivo del messaggio
        }
      });
    } catch (e) {
      debugPrint("Errore decodifica JSON pacchetto: $e");
    }
  }

  void gestisciTts(Map<String, dynamic> dati) {
    if (dati['tipo'] == 'TESTO' && dati.containsKey('contenuto')) {
      String contenuto = dati['contenuto'].toString();
      if (contenuto != ultimaLettura) {
        ultimaLettura = contenuto;
        flutterTts.speak(contenuto);
      }
    }
  }

  Widget _buildVisualContent(Map<String, dynamic> dati) {
    String tipo = dati['tipo'] ?? 'TESTO';

    switch (tipo) {
      case 'TABELLA':
        var contenuto = dati['contenuto'];
        // PROTEZIONE CRASH: se non è una lista, mostra il testo di fallback dell'agente senza crashare
        if (contenuto is! List) {
          return SizedBox.expand(
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.all(16.0),
              child: SelectableText(contenuto?.toString() ?? "Nessun dato tabella disponibile."),
            ),
          );
        }

        return SizedBox.expand(
          child: SingleChildScrollView(
            scrollDirection: Axis.vertical,
            physics: const BouncingScrollPhysics(),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              physics: const BouncingScrollPhysics(),
              child: DataTable(
                columns: const [DataColumn(label: Text('Info')), DataColumn(label: Text('Valore'))],
                // Aggiunto cast esplicito <DataRow> per evitare errori di compilazione/runtime
                rows: contenuto.map<DataRow>((r) {
                  String chiave = "";
                  String valore = "";
                  if (r is Map) {
                    chiave = r['chiave']?.toString() ?? '';
                    valore = r['valore']?.toString() ?? '';
                  } else {
                    chiave = "Dato";
                    valore = r.toString();
                  }
                  return DataRow(cells: [
                    DataCell(SelectableText(chiave)),
                    DataCell(SelectableText(valore))
                  ]);
                }).toList(),
              ),
            ),
          ),
        );
        
      case 'LISTA':
        var contenuto = dati['contenuto'];
        if (contenuto is! List) {
          return SizedBox.expand(
            child: SingleChildScrollView(
              physics: const BouncingScrollPhysics(),
              padding: const EdgeInsets.all(16.0),
              child: SelectableText(contenuto?.toString() ?? "Nessun elemento in lista."),
            ),
          );
        }

        return SizedBox.expand(
          child: ListView.builder(
            physics: const BouncingScrollPhysics(),
            // CORRETTO: rimosso l'ultimo "contenido" rimasto e sostituito con "contenuto"
            itemCount: contenuto.length,
            itemBuilder: (context, index) {
              final item = contenuto[index];
              String titolo = "";
              if (item is Map) {
                titolo = item['titolo']?.toString() ?? item['contenuto']?.toString() ?? '';
              } else {
                titolo = item.toString();
              }
              return ListTile(
                title: SelectableText(titolo),
                leading: const Icon(Icons.newspaper),
              );
            },
          ),
        );

      case 'POPUP':
        String titoloPopup = dati['titolo']?.toString() ?? "Notifica di Sistema";
        String messaggioPopup = dati['messaggio']?.toString() ?? dati['contenuto']?.toString() ?? "";
        return SizedBox.expand(
          child: SingleChildScrollView(
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.warning_amber_rounded, color: Colors.orangeAccent),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        titoloPopup, 
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.orangeAccent),
                        softWrap: true,
                      ),
                    ),
                  ],
                ),
                const Divider(color: Colors.orangeAccent),
                const SizedBox(height: 10),
                SelectableText(messaggioPopup, style: const TextStyle(fontSize: 16)),
              ],
            ),
          ),
        );
        
      default:
        return SizedBox.expand(
          child: SingleChildScrollView(
            scrollDirection: Axis.vertical,
            physics: const BouncingScrollPhysics(),
            padding: const EdgeInsets.all(16.0),
            child: SelectableText(
              dati['contenuto']?.toString() ?? "",
              style: const TextStyle(fontSize: 16),
            ),
          ),
        );
    }
  }

  @override
  void dispose() {
    // Chiusura pulita delle risorse all'uscita per evitare memory leak
    channel.sink.close();
    _inputController.dispose();
    flutterTts.stop();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (haErroreConnessione) {
      return const Scaffold(
        body: Center(
          child: Padding(
            padding: EdgeInsets.all(20.0),
            child: Text(
              "Errore di connessione al server SIA.\nVerifica che il backend Python sia attivo.", 
              textAlign: TextAlign.center, 
              style: TextStyle(color: Colors.redAccent, fontSize: 16)
            ),
          ),
        ),
      );
    }

    return Scaffold(
      resizeToAvoidBottomInset: true, 
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 10.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 10),
              Text(
                "SICUREZZA: $sicurezza", 
                style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              Text(
                "${cpuValue.toStringAsFixed(1)}% CPU", 
                style: const TextStyle(fontSize: 40, fontWeight: FontWeight.w500),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 15),
              // Area centrale dinamica protetta e flessibile senza limiti di spazio rigidi
              Expanded(
                child: Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.black12,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: _buildVisualContent(ultimiDatiVisuali),
                ),
              ),
              const SizedBox(height: 15),
              // Campo di input per l'invio dei comandi testuali
              TextField(
                controller: _inputController,
                decoration: InputDecoration(
                  hintText: 'Invia comando',
                  border: const OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: () {
                      if (_inputController.text.trim().isNotEmpty) {
                        channel.sink.add(jsonEncode({'comando_testuale': _inputController.text.trim()}));
                        _inputController.clear();
                      }
                    },
                  ),
                ),
                onSubmitted: (value) {
                  if (value.trim().isNotEmpty) {
                    channel.sink.add(jsonEncode({'comando_testuale': value.trim()}));
                    _inputController.clear();
                  }
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}