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
  String ultimaDomanda = "";

  @override
  void initState() {
    super.initState();
    channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8080'));
    initTts();
  }

  void initTts() async {
    await flutterTts.setLanguage("it-IT");
    await flutterTts.setSpeechRate(0.5);
  }

  void inviaComando(Map<String, dynamic> comando) {
    channel.sink.add(json.encode(comando));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          
          final Map<String, dynamic> dati = jsonDecode(snapshot.data);
          
          // 1. Gestione Feedback Server (Risposte alle tue domande o ricerche)
          if (dati.containsKey('feedback')) {
            flutterTts.speak(dati['feedback']);
          }

          // 2. Gestione Domande Proattive
          final domanda = dati['domanda'] ?? "";
          if (domanda != "Sistema ok." && domanda != ultimaDomanda) {
            ultimaDomanda = domanda;
            flutterTts.speak(domanda); 
          }

          return Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text("SICUREZZA: ${dati['sicurezza']}", style: const TextStyle(fontSize: 24)),
                Text("${dati['monitoraggio']['cpu'].toStringAsFixed(1)}% CPU", style: const TextStyle(fontSize: 50)),
                
                // Campo di Input per scrivere all'Agente
                TextField(
                  controller: _inputController,
                  decoration: InputDecoration(
                    hintText: "Scrivi un comando o una ricerca...",
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.send),
                      onPressed: () {
                        inviaComando({"comando_testuale": _inputController.text});
                        _inputController.clear();
                      },
                    ),
                  ),
                ),

                if (domanda != "Sistema ok." && domanda != "")
                  Column(
                    children: [
                      const SizedBox(height: 20),
                      Text(domanda, style: const TextStyle(color: Colors.yellow)),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          ElevatedButton(onPressed: () => inviaComando({"azione": "pulisci"}), child: const Text("SI")),
                          const SizedBox(width: 20),
                          ElevatedButton(onPressed: () => setState(() => ultimaDomanda = ""), child: const Text("NO")),
                        ],
                      ),
                    ],
                  ),
              ],
            ),
          );
        },
      ),
    );
  }

  @override
  void dispose() {
    channel.sink.close();
    flutterTts.stop();
    _inputController.dispose();
    super.dispose();
  }
}