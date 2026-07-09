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

  Widget _buildVisualContent(Map<String, dynamic> dati) {
    String tipo = dati['tipo'] ?? 'TESTO';
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
          child: Text(dati['contenuto']?.toString() ?? "In attesa..."),
        );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());
          
          Map<String, dynamic> dati;
          try {
            dati = jsonDecode(snapshot.data);
          } catch (e) {
            return const Center(child: Text("Errore dati"));
          }

          if (dati.containsKey('feedback')) flutterTts.speak(dati['feedback'].toString());
          final String content = dati['contenuto']?.toString() ?? "";
          if (content != "Sistema ok." && content != ultimaDomanda) {
            ultimaDomanda = content;
            flutterTts.speak(content);
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
                    hintText: "Scrivi un comando...",
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.send),
                      onPressed: () {
                        if (_inputController.text.isNotEmpty) {
                          channel.sink.add(jsonEncode({'comando_testuale': _inputController.text}));
                          _inputController.clear();
                        }
                      },
                    ),
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
