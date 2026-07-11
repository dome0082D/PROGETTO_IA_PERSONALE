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
  String ultimaLettura = ""; // Variabile rinominata per chiarezza

  @override
  void initState() {
    super.initState();
    // Il server è su ws://127.0.0.1:8080
    channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8080'));
    initTts();
  }

  void initTts() async {
    await flutterTts.setLanguage("it-IT");
    await flutterTts.setSpeechRate(0.5);
  }

  // LOGICA CORRETTA PER LA GESTIONE TTS
  void gestisciTts(Map<String, dynamic> dati) {
    if (dati.containsKey('tipo') && dati['tipo'] == 'TESTO' && dati.containsKey('contenuto')) {
      String contenuto = dati['contenuto'].toString();
      if (contenuto != ultimaLettura) {
        ultimaLettura = contenuto;
        flutterTts.speak(contenuto);
      }
    }
  }

  Widget _buildVisualContent(Map<String, dynamic> dati) {
    String tipo = dati['tipo'] ?? 'MONITOR';
    // Se è un monitoraggio, non mostriamo nulla o mostriamo un widget dedicato
    if (tipo == 'MONITOR') return const SizedBox.shrink();

    switch (tipo) {
      case 'TABELLA':
        return SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: DataTable(
            columns: const [DataColumn(label: Text('Info')), DataColumn(label: Text('Valore'))],
            rows: (dati['contenuto'] as List).map((r) => DataRow(cells: [
              DataCell(Text(r['chiave'].toString())),
              DataCell(Text(r['valore'].toString()))
            ])).toList(),
          ),
        );
      case 'LISTA':
        return ListView.builder(
          shrinkWrap: true,
          itemCount: (dati['contenuto'] as List).length,
          itemBuilder: (context, index) => ListTile(
            title: Text(dati['contenuto'][index]['titolo'] ?? ''),
            leading: const Icon(Icons.newspaper),
          ),
        );
      default:
        return Padding(
          padding: const EdgeInsets.all(16.0),
          child: Text(dati['contenuto']?.toString() ?? ""),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          if (snapshot.hasError) return const Center(child: Text("Errore connessione"));
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          
          Map<String, dynamic> dati;
          try {
            dati = jsonDecode(snapshot.data);
            gestisciTts(dati); // Chiamata separata sicura
          } catch (e) {
            return const Center(child: Text("Errore formattazione dati"));
          }

          final mon = dati.containsKey('monitoraggio') ? dati['monitoraggio'] : {'cpu': 0.0};
          final double cpuValue = (mon['cpu'] ?? 0.0).toDouble();

          return Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                const SizedBox(height: 50),
                Text("SICUREZZA: ${dati['sicurezza'] ?? 'NORMALE'}", style: const TextStyle(fontSize: 24)),
                Text("${cpuValue.toStringAsFixed(1)}% CPU", style: const TextStyle(fontSize: 40)),
                Expanded(child: _buildVisualContent(dati)),
                TextField(
                  controller: _inputController,
                  decoration: InputDecoration(
                    hintText: 'Invia comando',
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.send),
                      onPressed: () {
                        channel.sink.add(jsonEncode({'comando_testuale': _inputController.text}));
                        _inputController.clear();
                      },
                    ),
                  ),
                  onSubmitted: (value) {
                    channel.sink.add(jsonEncode({'comando_testuale': value}));
                    _inputController.clear();
                  },
                ),