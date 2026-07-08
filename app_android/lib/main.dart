import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:file_picker/file_picker.dart';
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          if (!snapshot.hasData) {
            return const Center(child: CircularProgressIndicator());
          }
          
          final Map<String, dynamic> dati = jsonDecode(snapshot.data);
          
          // GESTIONE VOCALE (Feedback e Domande)
          if (dati.containsKey('feedback')) {
            flutterTts.speak(dati['feedback'].toString());
          }
          final String domanda = dati['domanda'] ?? "";
          if (domanda != "Sistema ok." && domanda != ultimaDomanda) {
            ultimaDomanda = domanda;
            flutterTts.speak(domanda);
          }

          // Estrazione sicura CPU
          final mon = dati.containsKey('monitoraggio') ? dati['monitoraggio'] : {'cpu': 0.0};
          final double cpuValue = (mon['cpu'] ?? 0.0).toDouble();

          return Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text("SICUREZZA: ${dati['sicurezza'] ?? 'NORMALE'}", style: const TextStyle(fontSize: 24)),
                Text("${cpuValue.toStringAsFixed(1)}% CPU", style: const TextStyle(fontSize: 50)),
                
                const SizedBox(height: 30),
                
                TextField(
                  controller: _inputController,
                  decoration: InputDecoration(
                    hintText: "Scrivi un comando...",
                    suffixIcon: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: const Icon(Icons.attach_file),
                          onPressed: () async {
                            FilePickerResult? result = await FilePicker.platform.pickFiles();
                            if (result != null && result.files.single.path != null) {
                              String path = result.files.single.path!;
                              channel.sink.add(json.encode({"file_caricato": path}));
                            }
                          },
                        ),
                        IconButton(
                          icon: const Icon(Icons.send),
                          onPressed: () {
                            if (_inputController.text.isNotEmpty) {
                              channel.sink.add(json.encode({"comando_testuale": _inputController.text}));
                              _inputController.clear();
                            }
                          },
                        ),
                      ],
                    ),
                  ),
                ),
                
                // Pulsanti SI/NO per le risposte proatt