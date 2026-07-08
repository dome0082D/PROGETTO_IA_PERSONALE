import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:file_picker/file_picker.dart'; // Import per caricare le foto
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
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          
          final Map<String, dynamic> dati = jsonDecode(snapshot.data);
          
          // GESTIONE VOCALE SICURA
          if (dati.containsKey('feedback')) {
            flutterTts.speak(dati['feedback']);
          }
          final domanda = dati['domanda'] ?? "";
          if (domanda != "Sistema ok." && domanda != ultimaDomanda) {
            ultimaDomanda = domanda;
            flutterTts.speak(domanda);
          }

          // Estrazione sicura dei dati CPU
          final mon = dati.containsKey('monitoraggio') ? dati['monitoraggio'] : {'cpu': 0.0};
          final cpuValue = (mon['cpu'] ?? 0.0).toDouble();

          return Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text("SICUREZZA: ${dati['sicurezza'] ?? 'NORMALE'}", style: const TextStyle(fontSize: 24)),
                Text("${cpuValue.toStringAsFixed(1)}% CPU", style: const TextStyle(fontSize: 50)),
                
                const SizedBox(height: 30),
                
                // CAMPO DI INPUT CON AGGIUNTA CARICAMENTO FILE
                TextField(
                  controller: _inputController,
                  decoration: InputDecoration(
                    hintText: "Scrivi un comando o una ricerca...",
                    suffixIcon: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // Pulsante per caricare file (Fase 2)
                        IconButton(
                          icon: const Icon(Icons.attach_file),
                          onPressed: () async {
                            FilePickerResult? result = await FilePicker.platform.pickFiles();
                            if (result != null) {
                              String path = result.files.single.path!;
                              channel.sink.add(json.encode({"file_caricato": path}));
                            }
                          },
                        ),
                        // Pulsante invio testo
                        IconButton(
                          icon: const Icon(Icons.send),
                          onPressed: () {
                            channel.sink.add(json.encode({"comando_testuale": _inputController.text}));
                            _inputController.clear();
                          },
                        ),
                      ],
                    ),
                  ),
                ),
                
                // PULSANTI (S