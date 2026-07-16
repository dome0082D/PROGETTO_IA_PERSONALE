// lib/main.dart
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:audioplayers/audioplayers.dart';
import 'dart:convert';
import 'dart:typed_data';

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
  final AudioPlayer audioPlayer = AudioPlayer(); 
  final TextEditingController _inputController = TextEditingController();
  final ScrollController _scrollController = ScrollController(); // Per scorrere in basso automaticamente
  
  // VARIABILI DI STATO PERSISTENTI
  String sicurezza = "OPERATIVO";
  double cpuValue = 0.0;
  bool haErroreConnessione = false;
  
  // NUOVE VARIABILI DI STATO
  bool isMuted = false; 
  String dataOra = "--/--/---- --:--";
  String ultimaLettura = ""; 
  
  // LA NUOVA MEMORIA A SCHERMO: Una lista che conserva tutto
  List<Map<String, dynamic>> cronologia = [];

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
          setState(() { haErroreConnessione = true; });
        },
        onDone: () {
          debugPrint("Connessione WebSocket chiusa.");
        },
      );
    } catch (e) {
      setState(() { haErroreConnessione = true; });
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
        
        // 2. Aggiornamento dati di monitoraggio e orologio
        if (dati.containsKey('monitoraggio')) {
          final mon = dati['monitoraggio'];
          if (mon is Map) {
            if (mon.containsKey('cpu')) cpuValue = (mon['cpu'] ?? 0.0).toDouble();
            if (mon.containsKey('timestamp')) {
              dataOra = "${mon['timestamp']['data']} ${mon['timestamp']['ora']}";
            }
          }
        }
        
        // 3. Gestione Cronologia: se il server manda l'intera memoria, aggiorniamo la lista
        if (dati.containsKey('cronologia')) {
          cronologia = List<Map<String, dynamic>>.from(dati['cronologia']);
          _scrollToBottom();
        } 
        // 4. Gestione Singolo Messaggio Visivo (fallback se il server non manda tutta la cronologia)
        else {
          String? tipo = dati['tipo'];
          if (tipo != null && tipo != 'MONITOR') {
            cronologia.add(dati);
            _scrollToBottom();
            gestisciOutputAudio(dati); 
          }
        }
      });
    } catch (e) {
      debugPrint("Errore decodifica JSON pacchetto: $e");
    }
  }

  Future<void> gestisciOutputAudio(Map<String, dynamic> dati) async {
    if (isMuted) return; // Se il Mute è attivo, ignora l'audio

    // 1. Audio ad alta qualità (MP3) dal server
    if (dati.containsKey('audio_base64') && dati['audio_base64'] != null) {
      try {
        Uint8List bytes = base64Decode(dati['audio_base64']);
        await audioPlayer.play(BytesSource(bytes));
      } catch (e) {
        debugPrint("Errore riproduzione audio MP3: $e");
      }
    } 
    // 2. Fallback di sicurezza al vecchio TTS testuale se manca l'audio neurale
    else if (dati['tipo'] == 'TESTO' && dati.containsKey('contenuto')) {
      String contenuto = dati['contenuto'].toString();
      if (contenuto != ultimaLettura) {
        ultimaLettura = contenuto;
        await flutterTts.speak(contenuto);
      }
    }
  }

  void _scrollToBottom() {
    Future.delayed(const Duration(milliseconds: 100), () {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  // Costruisce i widget visivi proteggendo e mantenendo tutta la tua logica precedente
  Widget _buildVisualContent(Map<String, dynamic> dati) {
    String tipo = dati['tipo'] ?? 'TESTO';
    String mittente = dati['autore'] ?? (dati['input'] != null ? 'Utente' : 'SIA');
    
    // Header che indica chi ha scritto (Utente o SIA)
    Widget header = Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Text(
        mittente.toUpperCase(),
        style: TextStyle(
          fontWeight: FontWeight.bold,
          color: mittente == 'Utente' ? Colors.blueAccent : Colors.greenAccent,
        ),
      ),
    );

    Widget contenutoWidget;

    switch (tipo) {
      case 'TABELLA':
        var contenuto = dati['contenuto'];
        if (contenuto is! List) {
          contenutoWidget = SelectableText(contenuto?.toString() ?? "Nessun dato tabella disponibile.");
        } else {
          contenutoWidget = SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            physics: const BouncingScrollPhysics(),
            child: DataTable(
              columns: const [DataColumn(label: Text('Info')), DataColumn(label: Text('Valore'))],
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
          );
        }
        break;
        
      case 'LISTA':
        var contenuto = dati['contenuto'];
        if (contenuto is! List) {
          contenutoWidget = SelectableText(contenuto?.toString() ?? "Nessun elemento in lista.");
        } else {
          contenutoWidget = Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            // Sostituisco la ListView interna con una Column per non rompere la ListView principale esterna
            children: contenuto.map<Widget>((item) {
              String titolo = "";
              if (item is Map) {
                titolo = item['titolo']?.toString() ?? item['contenuto']?.toString() ?? '';
              } else {
                titolo = item.toString();
              }
              return ListTile(
                title: SelectableText(titolo),
                leading: const Icon(Icons.newspaper),
                dense: true, // Rende la lista più compatta
              );
            }).toList(),
          );
        }
        break;

      case 'POPUP':
        String titoloPopup = dati['titolo']?.toString() ?? "Notifica di Sistema";
        String messaggioPopup = dati['messaggio']?.toString() ?? dati['contenuto']?.toString() ?? "";
        contenutoWidget = Column(
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
        );
        break;
        
      default: // TESTO
        String testoVisivo = dati['input'] ?? dati['risposta'] ?? dati['contenuto']?.toString() ?? "";
        contenutoWidget = SelectableText(
          testoVisivo,
          style: const TextStyle(fontSize: 16),
        );
    }

    // Incapsula ogni messaggio nel suo "fumetto" per renderlo ben visibile
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0),
      padding: const EdgeInsets.all(12.0),
      decoration: BoxDecoration(
        color: Colors.black26,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [header, contenutoWidget],
      ),
    );
  }

  @override
  void dispose() {
    // Chiusura pulita delle risorse all'uscita per evitare memory leak
    channel.sink.close();
    _inputController.dispose();
    _scrollController.dispose();
    flutterTts.stop();
    audioPlayer.dispose();
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
              // 1. NUOVO HEADER CON TASTO MUTE E OROLOGIO
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(dataOra, style: const TextStyle(color: Colors.grey, fontSize: 14)),
                  IconButton(
                    icon: Icon(isMuted ? Icons.volume_off : Icons.volume_up, 
                               color: isMuted ? Colors.redAccent : Colors.greenAccent, size: 30),
                    onPressed: () async {
                      setState(() { isMuted = !isMuted; });
                      if (isMuted) {
                        await audioPlayer.stop();
                        await flutterTts.stop();
                      }
                    },
                    tooltip: "Pausa/Mute Audio",
                  ),
                ],
              ),
              const SizedBox(height: 5),
              // 2. DATI DI MONITORAGGIO GLOBALI
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
              
              // 3. AREA CENTRALE CON LA CRONOLOGIA COMPLETA
              Expanded(
                child: Container(
                  width: double.infinity,
                  decoration: BoxDecoration(
                    color: Colors.black12,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: cronologia.isEmpty 
                    ? const Center(child: Text("SIA Connessa. In attesa di comandi...", style: TextStyle(color: Colors.grey)))
                    : ListView.builder(
                        controller: _scrollController,
                        physics: const BouncingScrollPhysics(),
                        padding: const EdgeInsets.all(8.0),
                        itemCount: cronologia.length,
                        itemBuilder: (context, index) {
                          return _buildVisualContent(cronologia[index]);
                        },
                      ),
                ),
              ),
              const SizedBox(height: 15),
              
              // 4. CAMPO DI INPUT TESTUALE
              TextField(
                controller: _inputController,
                decoration: InputDecoration(
                  hintText: 'Invia comando',
                  border: const OutlineInputBorder(),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: () {
                      if (_inputController.text.trim().isNotEmpty) {
                        // Visualizza immediatamente il testo a schermo prima di inviarlo
                        setState(() {
                          cronologia.add({
                            'tipo': 'TESTO',
                            'autore': 'Utente',
                            'contenuto': _inputController.text.trim()
                          });
                          _scrollToBottom();
                        });
                        channel.sink.add(jsonEncode({'comando_testuale': _inputController.text.trim()}));
                        _inputController.clear();
                      }
                    },
                  ),
                ),
                onSubmitted: (value) {
                  if (value.trim().isNotEmpty) {
                    // Visualizza immediatamente il testo a schermo prima di inviarlo
                    setState(() {
                      cronologia.add({
                        'tipo': 'TESTO',
                        'autore': 'Utente',
                        'contenuto': value.trim()
                      });
                      _scrollToBottom();
                    });
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