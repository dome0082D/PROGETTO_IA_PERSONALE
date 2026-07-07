import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'IA Personale Totale',
      theme: ThemeData(brightness: Brightness.dark, useMaterial3: true),
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

  @override
  void initState() {
    super.initState();
    channel = WebSocketChannel.connect(Uri.parse('ws://127.0.0.1:8080'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("IA Personale - Centro di Controllo")),
      body: StreamBuilder(
        stream: channel.stream,
        builder: (context, snapshot) {
          if (snapshot.hasError) return Center(child: Text('Errore: ${snapshot.error}'));
          if (!snapshot.hasData) return const Center(child: CircularProgressIndicator());

          final Map<String, dynamic> dati = jsonDecode(snapshot.data);
          final mon = dati['monitoraggio'];
          
          return Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // --- Equalizzatore / Riga Viva ---
                Container(
                  height: 10,
                  width: (mon['cpu'] * 5).toDouble(),
                  decoration: BoxDecoration(
                    color: dati['sicurezza'] == "NORMALE" ? Colors.blue : Colors.red,
                    borderRadius: BorderRadius.circular(5)
                  ),
                ),
                const SizedBox(height: 30),
                
                Text("SICUREZZA: ${dati['sicurezza']}", style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                Text("VISIONE: ${dati['visione']}", style: const TextStyle(fontSize: 18, color: Colors.grey)),
                
                const Divider(height: 40),
                
                Text("CPU: ${mon['cpu'].toStringAsFixed(1)}%", style: const TextStyle(fontSize: 50)),
                
                const SizedBox(height: 20),
                const Text("Tutti i sistemi sono online e modulari."),
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
    super.dispose();
  }
}